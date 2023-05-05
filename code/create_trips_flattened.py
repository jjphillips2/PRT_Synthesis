#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Purpose: Create flattened trip dataset. Resulting dataset is at trip_id level.
"""

import pandas as pd
import numpy as np
import datetime as datetime
from matplotlib import pyplot as plt

### helper function to import code if needed
def open_file(path):
    dataDict = {}
    with open(path) as f: 
        lines = f.readlines()
        df_columns = lines[0].strip('\n').split(',')
        for i, line in enumerate(lines): 
            if i > 0: 
                row = line.strip('\n').split(',')
                dataDict['row'+str(i)] = row


    dataDF = pd.DataFrame.from_dict(dataDict, orient='index', columns = df_columns).reset_index(drop = True)
    return(dataDF)


path = '/Users/sumati/Documents/CMU/Academics/Spring2023/Capstone/code/data'
# read in trips
trips = pd.read_csv(path+'/GTFS_2022/trips.csv')
trips = trips[~trips.trip_id.str.contains('Rail')] # remove rail/incline
print(trips.shape)
trips.head()

# read in stop times
stop_times = pd.read_csv(path+'/GTFS_2022/stop_times.csv')
print(stop_times.shape)
stop_times.trip_id = stop_times.trip_id.apply(lambda x: str(x))
stop_times.stop_id = stop_times.stop_id.apply(lambda x: str(x))
stop_times.head()

# merge stops with stoptimes to add lat/long
stops = pd.read_csv(path+'/GTFS_2022/stops.csv')
stops = stops[['stop_id', 'stop_name']]
print(stops.shape)
stops.head()

# merge stops with stop times to add geography
stop_times_w_stopnames = pd.merge(stop_times, stops, on = 'stop_id', how = 'left')
print(stop_times_w_stopnames.shape)
stop_times_w_stopnames.head()

# merge stop times with trips to get trip duration and sequence 
tripCols = ['trip_id', 'block_id', 'route_id','trip_headsign', 'service_id']
stoptimesCols = ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence', 
                 'stop_name','shape_dist_traveled']
tripTimes = pd.merge(trips[tripCols], stop_times_w_stopnames[stoptimesCols], how = 'inner', on = 'trip_id')
#tripTimes = tripTimes[tripTimes.route_id.apply(lambda x: x in ['71C', '82'])]
print(tripTimes.shape)

# look into total block duration and trip duration -- trip starts
tripStarts = tripTimes.sort_values(by = ['trip_id', 'block_id', 'stop_sequence']).groupby(['trip_id', 'block_id']).head(1)[['trip_id', 'block_id', 'route_id', 'trip_headsign', 'departure_time', 'service_id', 'stop_name', 'stop_id']]
tripStarts.rename(columns = {'departure_time': 'trip_start_time',
                            'service_id': 'service_id_start',
                            'stop_name':'start_stop',
                            'stop_id': 'start_stop_id'}, inplace = True)
print(tripStarts.shape)

# look into total block duration and trip duration -- trip ends
tripEnds = tripTimes.sort_values(by = ['trip_id', 'block_id', 'stop_sequence']).groupby(['trip_id', 'block_id']).tail(1)[['trip_id', 'block_id', 'route_id', 'departure_time', 'stop_sequence', 'shape_dist_traveled', 'service_id', 'stop_name', 'stop_id']]
tripEnds.rename(columns = {'departure_time':'trip_end_time',
                           'stop_sequence': 'number_total_stops', 
                           'shape_dist_traveled': 'total_distance_traveled', 
                          'service_id': 'service_id_end', 
                          'stop_name': 'end_stop',
                          'stop_id':'end_stop_id'}, inplace = True)
print(tripEnds.shape)

# dataset at trip-block level with the start/end time for each trip, and total distance traveled 
tripWide = pd.merge(tripStarts, tripEnds, on = ['trip_id', 'block_id', 'route_id'], how = 'inner')
tripWide.sort_values(['block_id', 'trip_id']).head(5)




# adjust time variables so that they can be converted to datetime, calculate trip time deltas
for i in range(len(tripWide)):
    if int(tripWide.loc[i, 'trip_start_time'][0:2]) < 24:
        tripWide.loc[i, 'trip_start_datetime'] = "01/01/23 "+tripWide.loc[i, 'trip_start_time']
    else: 
        diff = str(abs(24 - int(tripWide.loc[i, 'trip_start_time'][0:2])))
        diff_fmt = diff.rjust(2, '0')
        tripWide.loc[i, 'trip_start_datetime'] = "01/02/23 "+diff_fmt+tripWide.loc[i, 'trip_start_time'][2:]
        
    if int(tripWide.loc[i, 'trip_end_time'][0:2]) < 24: 
        tripWide.loc[i, 'trip_end_datetime'] = "01/01/23 "+tripWide.loc[i, 'trip_end_time'] 
    else: 
        diff = str(abs(24 - int(tripWide.loc[i, 'trip_end_time'][0:2])))
        diff_fmt = diff.rjust(2, '0')
        tripWide.loc[i, 'trip_end_datetime'] = "01/02/23 "+diff_fmt+tripWide.loc[i, 'trip_end_time'][2:]
        
    tripWide.loc[i, 'trip_start_datetime'] = datetime.datetime.strptime(tripWide.loc[i, 'trip_start_datetime'], '%m/%d/%y %H:%M:%S')
    tripWide.loc[i, 'trip_end_datetime'] = datetime.datetime.strptime(tripWide.loc[i, 'trip_end_datetime'], '%m/%d/%y %H:%M:%S')
    
    tripWide.loc[i, 'timeDelta'] = tripWide.loc[i, 'trip_end_datetime'] - tripWide.loc[i, 'trip_start_datetime']
    tripWide.loc[i, 'timeDelta_minutes'] = tripWide.loc[i, 'timeDelta'].seconds / 60
    tripWide.loc[i, 'timeDelta_hours'] = tripWide.loc[i, 'timeDelta_minutes']/60
  
    
  
# exclude incline/rail
excludeRoutes = ['DQI-199', 'MI-199', 'RED-199', 'SLVR-199', 'BLUE-199']
tripWide = tripWide[tripWide.route_id.apply(lambda x: x not in excludeRoutes)]
tripWide.shape
  
# output for all routes
tripWide.total_distance_traveled = tripWide.total_distance_traveled.apply(lambda x: x/1609.34) # convert to miles
tripWide.head()[['block_id', 'trip_id', 'trip_start_time', 'trip_end_time', 'total_distance_traveled']]
tripWide = tripWide.sort_values(['block_id', 'trip_start_datetime']).reset_index(drop = True)
tripWide.to_csv('trips_flattened_allRoutes.csv')
   
 
# filter for routes from east liberty garage 
east_lib_routes = ['71A','71D','74','89','P2','P78','P1','71B','88','68','69','71','77','86',
                   '87','P68','P69','P71','75','67','P12','P16','P67','28X','79','82','P17','71C','58']

eastLibTrips = tripWide.copy()

eastLibTrips = eastLibTrips[eastLibTrips.route_id.apply(lambda x: x in east_lib_routes)]
eastLibTrips = eastLibTrips.sort_values(['block_id', 'trip_start_datetime']).reset_index(drop = True)


# output
eastLibTrips.to_csv('data/trips_flattened_eastLibRoutes.csv')



# updating total distance from meters to miles 
trips_flattened = pd.read_csv('/Users/sumati/Documents/CMU/Academics/Spring2023/Capstone/code/data/trips_flattened_eastLibRoutes.csv')

trips_flattened.total_distance_traveled = trips_flattened.total_distance_traveled.apply(lambda x: x/1609.34)

trips_flattened.head()[['block_id', 'trip_id', 'trip_start_time', 'trip_end_time', 'total_distance_traveled']]

# output
trips_flattened.to_csv('/Users/sumati/Documents/CMU/Academics/Spring2023/Capstone/code/data/trips_flattened_eastLibRoutes_miles.csv')
