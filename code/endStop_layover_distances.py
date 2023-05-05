#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get distance from common end stops to each layover location

"""

import pandas as pd
import googlemaps
import numpy as np

# layover stops
layovers = pd.read_csv('LayoverLocations.csv')
layovers = layovers[['StopID', 'CleverID', 'Latitude', 'Longitude']]
layovers = layovers[~pd.isna(layovers.StopID)].reset_index(drop = True)
layovers.Latitude = layovers.Latitude.apply(lambda x: float(x))
layovers.Longitude = layovers.Longitude.apply(lambda x: float(x))
layovers.CleverID = layovers.CleverID.apply(lambda x: str(x))
layover_stops_ordered = np.array(layovers.StopID)
layo.l

# flagged end stops 
stops = [4405, 8308, 16063, 22873, 16111, 8812, 19687, 15276, 22326, 3302, 21624, 1407]
stops = [str(x) for x in stops]

data_path = '/Users/sumati/Documents/CMU/Academics/Spring2023/Capstone/code/data/GTFS_2022'
stops_gtfs = pd.read_csv(data_path+'/stops.csv')[['stop_id', 'stop_lat', 'stop_lon']]
stops_gtfs.head()


# filter for just end stops
end_stops = stops_gtfs.copy()
end_stops = end_stops[end_stops.stop_id.apply(lambda x: x in stops)].reset_index(drop = True)
end_stops.shape
end_stops_ordered = np.array(end_stops.stop_id)
        
        
## Google API Code--thanks Josh! 

gmaps = googlemaps.Client(key='AIzaSyCkPwCy_xhDTMrzQ2W2dyXnFQWN-3g6KRc') #make sure to switch to your API key if mine doesn't work

#df = pd.read_csv('your_dataframe.csv') # your csv/path

def get_distance(lat1, lon1, lat2, lon2):
    origin = str(lat1) + ',' + str(lon1)
    destination = str(lat2) + ',' + str(lon2)
    result = gmaps.distance_matrix(origin, destination, mode='driving', units = 'imperial')
    distance = result['rows'][0]['elements'][0]['distance']['value'] / 1609.34 # convert meters to miles 
    return distance

def get_time(lat1, lon1, lat2, lon2):
    origin = str(lat1) + ',' + str(lon1)
    destination = str(lat2) + ',' + str(lon2)
    result = gmaps.distance_matrix(origin, destination, mode='driving', units = 'imperial')
    distance = result['rows'][0]['elements'][0]['duration']['value'] / 60 # convert meters to miles 
    return distance

# create end stops - layover distance matrix 
distance_matrix = np.zeros([len(end_stops), len(layovers)])
# calculate distance from end stop to layover for each end point/layover combination
for i in range(len(layovers)):
    for j in range(len(end_stops)):
        lat_i, lon_i = layovers.loc[i, 'Latitude'], layovers.loc[i, 'Longitude']
        lat_j, lon_j = end_stops.loc[j, 'stop_lat'], end_stops.loc[j, 'stop_lon']
        distance_matrix[j, i] = get_distance(lat_i, lon_i, lat_j, lon_j)



travel_time = np.zeros([len(end_stops), len(layovers)])

# calculate distance from end stop to layover for each end point/layover combination
for i in range(len(layovers)):
    for j in range(len(end_stops)):
        lat_i, lon_i = layovers.loc[i, 'Latitude'], layovers.loc[i, 'Longitude']
        lat_j, lon_j = end_stops.loc[j, 'stop_lat'], end_stops.loc[j, 'stop_lon']
        travel_time[j, i] = get_time(lat_i, lon_i, lat_j, lon_j)
        
travelTimeDF = pd.DataFrame(travel_time, index = end_stops_ordered, columns = layover_stops_ordered)
travelTimeDF.to_csv('stop_to_layover_travelTime.csv')
        
        
travel_time

# for each end stop, sort the layover stops by distance (shortest first)
end_stop_layover_dict = {}
for i in range(len(end_stops)):
    end_stop_layover_list = []
    distance_sorted_idx = np.argsort(distance_matrix[i, ])
    for j in range(5):
        end_stop_layover_list.append({layover_stops_ordered[distance_sorted_idx[j]]:distance_matrix[i, distance_sorted_idx[j]]})
    
    end_stop_layover_dict[end_stops_ordered[i]] = end_stop_layover_list
    
    
# convert to data frame
data_dict = {}
for i in range(len(end_stops_ordered)):
    for j in range(5):
        data_dict['row'+str(i)+str(j)] = [end_stops_ordered[i], 
                                       j+1, 
                                       list(end_stop_layover_dict[end_stops_ordered[i]][j].items())[0][0],
                                       list(end_stop_layover_dict[end_stops_ordered[i]][j].items())[0][1]
                                       ]
        
        
end_stop_potential_layovers = pd.DataFrame.from_dict(data_dict, orient='index')
end_stop_potential_layovers.reset_index(drop = True, inplace = True)
end_stop_potential_layovers.columns = ['EndStopID', 'DistanceRank', 'LayoverID', 'DistanceMiles']
end_stop_potential_layovers










# =============================================================================
# for index, row in df.iterrows():
#     lat1, lon1 = row['start_lat'], row['start_lon']
#     lat2, lon2 = row['end_lat'], row['end_lon']
#     walking_distance = get_walking_distance(lat1, lon1, lat2, lon2)
#     df.loc[index, 'walking_distance'] = walking_distance
# 
# 
# df.to_csv('your_dataframe_with_walking_distance.csv', index=False)
# =============================================================================
