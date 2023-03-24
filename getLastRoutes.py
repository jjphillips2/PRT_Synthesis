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


# import output file 

# INPUT: keep track of run criteria
eval_type = 'wc'
season = 'Winter'

# read stops dataset

# read in output from BusMileage.py
blocks_to_charge = pd.read_csv('blocks_needing_charge.csv')
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

failed_trips_id = tripFails

# for each trip, get the index where it failed, and return the previous trip
# this represents the last completed trip before requiring charge 

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


keep_vars = ['block_id','trip_id','route_id','trip_start_time','trip_end_time',
             'total_distance_traveled','timeDelta_minutes','trip_headsign',
             'start_stop','start_stop_id','end_stop','end_stop_id']


# output
#save_file_path_name = 'last_routes_'+season+"_"+eval_type+'.csv'
save_file_path_name = 'last_layover_routes_'+season+"_"+eval_type+'.csv'
last_route_per_block[keep_vars].to_csv(save_file_path_name)


## read in and analyze
winter_reg = pd.read_csv('last_layover_routes_Winter_reg.csv')
summer_reg = pd.read_csv('last_layover_routes_Summer_reg.csv')
winter_wc = pd.read_csv('last_layover_routes_Winter_wc.csv')
summer_wc = pd.read_csv('last_layover_routes_Summer_wc.csv')

    
lastLayoverRoutes = pd.concat([winter_reg, summer_reg, winter_wc, summer_wc])

np.unique(lastLayoverRoutes.trip_headsign)
np.unique(lastLayoverRoutes.route_id)
lastLayoverRoutes.groupby(['trip_headsign', 'route_id'])['block_id'].count().sort_values()   








