#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Converting output of BusMileage.py to GIS friendly output

Using the output of BusMileage.py (blocks_needing_charge) to keep the routes before failure for each block.
Thus, the dataset should be unique by block. 

Note right now (pre-midterm) we are not considering the effects of charging. 

# run after running BusMileage.py

"""


import pandas as pd
import numpy as np
import datetime as datetime

# read stops dataset

# read in output from BusMileage.py
blocks_to_charge = pd.read_csv('blocks_needing_charge.csv') # output from BusMileage.py
blocks_to_charge.shape
len(np.unique(blocks_to_charge.block_id))

# convert datetime objects
blocks_to_charge.trip_start_datetime = blocks_to_charge.trip_start_datetime.apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
blocks_to_charge.trip_end_datetime = blocks_to_charge.trip_end_datetime.apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

# identify layover trips
df_w_layover = pd.DataFrame()
for block in np.unique(blocks_to_charge.block_id):
    df_block = blocks_to_charge.copy()
    df_block = df_block[df_block.block_id == block].reset_index(drop = True)
    if df_block.shape[0] > 1:
        for i in range(len(df_block)-1):
            if (df_block.loc[i+1, 'trip_start_datetime'] - df_block.loc[i, 'trip_end_datetime']).seconds > 300:
                df_block.loc[i, 'layoverEndStop'] = 1
            else: 
                df_block.loc[i, 'layoverEndStop'] = 0
        df_w_layover = pd.concat([df_w_layover, df_block])

df_w_layover = df_w_layover.reset_index(drop = True)
df_w_layover.shape

failed_trips_id = tripFails # from BusMileage.py

# for each trip, get the index where it failed, and return the previous trip
# this represents the last completed trip before requiring charge (subtract 1 to get the previous stop if not a layover)
last_route_idx = []
for trip in failed_trips_id: 
    failure_idx = np.where(df_w_layover.trip_id == trip)[0][0]
    if df_w_layover.loc[failure_idx-1, 'layoverEndStop'] == 1:
        last_route_idx.append(failure_idx-1)
    else: 
        last_route_idx.append(failure_idx-2)
    
last_route_per_block = df_w_layover.copy()
last_route_per_block = last_route_per_block.iloc[last_route_idx]

# check what routes/directions are represented
np.unique(last_route_per_block.trip_headsign)
np.unique(last_route_per_block.route_id)
last_route_per_block.groupby(['trip_headsign', 'route_id'])['block_id'].count().sort_values()   
last_route_per_block.groupby('route_id')['block_id'].count()
# look at end stops
last_route_per_block.groupby(['trip_headsign', 'end_stop_id'])['block_id'].count().sort_values()   
np.unique(last_route_per_block.end_stop_id)




# code for outputs
keep_vars = ['block_id','trip_id','route_id','trip_start_time','trip_end_time',
             'total_distance_traveled','timeDelta_minutes','trip_headsign',
             'start_stop','start_stop_id','end_stop','end_stop_id']

# store and analyze together
winterResults = last_route_per_block.copy()
winterResults['Season'] = 'Winter'
winterResults.groupby(['trip_headsign', 'route_id'])['block_id'].count().sort_values()   

summerResults = last_route_per_block.copy()
summerResults['Season'] = 'Summer'

allResults = pd.concat([winterResults, summerResults])
allResults.groupby(['trip_headsign', 'route_id'])['block_id'].count().sort_values(ascending = False)   
np.unique(allResults.end_stop_id)


allResults[keep_vars].to_csv('lastRoutes_EL_distance.csv')




# read in and analyze across routes
dist = pd.read_csv('lastRoutes_all_distance.csv')
time = pd.read_csv('lastRoutes_all_time.csv')
distTime = pd.read_csv('lastRoutes_all_distancetime.csv')

allData = pd.concat([dist, time, distTime])
allData['end_stop_id'] = allData['end_stop_id'].apply(lambda x: str(x))
allData.groupby(['route_id', 'end_stop_id', 'trip_headsign'], 
                as_index = False)['block_id'].count().sort_values(by = 'block_id', ascending = False)



el_dist = pd.read_csv('lastRoutes_EL_distance.csv')
el_time = pd.read_csv('lastRoutes_EL_time.csv')
el_distTime = pd.read_csv('lastRoutes_EL_distancetime.csv')

allELData = pd.concat([el_dist, el_time, el_distTime])
allELData['end_stop_id'] = allELData['end_stop_id'].apply(lambda x: str(x))
allELData.groupby(['route_id', 'end_stop_id', 'trip_headsign'], 
                as_index = False)['block_id'].count().sort_values(by = 'block_id', ascending = False)




## adding geo to the stops
path = '/Users/sumati/Documents/CMU/Academics/Spring2023/Capstone/code/data'
stops = pd.read_csv(path+'/GTFS_2022/stops.csv')
stops = stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']]


allStops = allData.groupby(['route_id', 'end_stop_id', 'trip_headsign'], 
                as_index = False)['block_id'].count().sort_values(by = 'block_id', ascending = False).reset_index(drop = True)
allStops = pd.merge(allStops, stops, how = 'left', left_on = 'end_stop_id', right_on = 'stop_id')
allStops.rename(columns = {'block_id': 'blockCount'}, inplace = True)
allStops
allStops.to_csv('all_failed_stops.csv')

ELStops = allELData.groupby(['route_id', 'end_stop_id', 'trip_headsign'], 
                as_index = False)['block_id'].count().sort_values(by = 'block_id', ascending = False)

ELStops = pd.merge(ELStops, stops, how = 'left', left_on = 'end_stop_id', right_on = 'stop_id')
ELStops.rename(columns = {'block_id': 'blockCount'}, inplace = True)
ELStops
ELStops.to_csv('EastLib_failed_stops.csv')




EL_blocks = np.unique(allELData.block_id)
allBlocks = np.unique(allData.block_id)

# failed blocks in all data that aren't in the east liberty list 
all_only = []
for block in allBlocks: 
    if block not in EL_blocks: 
        print(block)
        all_only.append(block)

# read in trips_flattened_allRoutes.csv
trips = pd.read_csv('trips_flattened_allRoutes.csv')
trips[trips.block_id.apply(lambda x: x in all_only)].groupby('route_id')['block_id'].count().sort_values(ascending = False)
        
# failed blocks in east liberty list not in overall list
for block in EL_blocks: 
    if block not in allBlocks: 
        print(block)


### ALL FAILED BLOCKS IN EAST LIBERTY ALSO FAIL OVERALL. 





