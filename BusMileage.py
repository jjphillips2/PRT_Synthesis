#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bus Mileage Tracker

"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# create Bus class
class Bus: 
    """
    Bus class will be specific to the current block specified. 
    
    Attributes of the class include: 
        - current charge 
        - charge profile
    """
    
    def __init__(self):
        self.current_charge_pct = None
        self.mileage_remaining = None
        self.block_id = None
        
 # create Trip class       
class Trip: 
    """
    Trip class will include the following attributes: 
        - trip_id
        - route_id
        - start_time
        - end_time
        - total_distance travlled
        - mileage/charge required
    
    """
    def __init__(self):
        self.trip_id = None
        self.route_id = None
        self.start_time = None
        self.end_time = None
        self.total_trip_distance = None
        self.mileage_required = None
        self.charge_required = None
        
# function to get the amount of charge required to complete a specified route--TBD       
def get_charge_required(route_id):
    '''
    Parameters
    ----------
    route_id : str
    
    Purpose
    --------
    Takes the route ID and calculates the battery charge required to complete the route

    Returns
    -------
    float: battery percentage required to complete the specified route
    '''
    pass

# function to get the amount of mileage required to compelte a specified route--TBD
def get_mileage_required(route_id):
    '''
    Parameters
    ----------
    route_id : str
        
    Purpose
    --------
    Takes the route ID and calculates the mileage required to complete the route

    Returns
    -------
    float: mileage required to complete the specified route
    '''
    pass

# function to conduct checks at the start of each trip for a block, flags when charging layover is needed
def charge_status_via_trip_completion(trips_flattened_df, blockID, start_charge_pct, max_mileage,
                                      min_charge_threshold, min_mileage_threshold):
    '''
    Parameters
    ----------
    trips_flattened_df : dataframe
        output of the create_trips_flattened.py file, block-trip level dataset on the drive.
    blockID : float
        global var, block ID of interest.
    start_charge_pct : float
        global var, charging pct of bus at "full charge"
    max_mileage : float
        global var, total mileage of bus at "full charge".
    min_charge_threshold : float
        global var, min allowed charge for bus to take a trip.
    min_mileage_threshold : float
        global var, min allowed mileage for bus to take a trip.
        
    Purpose
    --------
    For each trip in a block, assess whether bus can complete trip before hitting minimum
    threshold for charge/mileage. Identifies when charging layovers should be complete. 
    Assumes within-trip charging not allowed. 

    Returns
    -------
    Prints whether bus can complete a trip, and at what point to have a charging layover.
    Prints line graph of charging profile x trip.

    '''
    # initialize bus parameters
    bus = Bus()
    bus.current_charge_pct = start_charge_pct
    bus.mileage_remaining = max_mileage
    bus.block_id = blockID
    
    # get trip list based on block_id
    trips = trips_flattened_df[trips_flattened_df.block_id == blockID].trip_id.tolist()
    
    # initialize array to keep track of charge for plotting charge depletion x trip 
    charging_profile = [start_charge_pct]
    mileage_profile = [max_mileage]
    # for each trip in the specified block, store the relevant attributes, and check whether remaining charge/mileage is sufficient to complete next trip
    for i, t in enumerate(trips): 
        trips_complete = 0
        trip_df = trips_flattened_df[(trips_flattened_df.block_id == blockID) & 
                                     (trips_flattened_df.trip_id == t)]
        trip = Trip()
        trip.trip_id = t
        trip.route_id = trip_df.route_id.iloc[0]
        trip.start_time = trip_df.trip_start_time.iloc[0]
        trip.end_time = trip_df.trip_end_time.iloc[0]
        trip.total_trip_distance = trip_df.total_distance_traveled.iloc[0]
        trip.mileage_required = get_mileage_required(trip.route_id)
        trip.charge_required = get_charge_required(trip.route_id)
        
        charge_depletion = bus.current_charge_pct - trip.charge_required 
        mileage_depletion = bus.mileage_remaining - trip.mileage_required 
        
        charging_profile.append(charge_depletion)
        mileage_profile.append(mileage_depletion)
        
        # if remaining charge/mileage is insuffiecient, break and charge battery
        if (charge_depletion < min_charge_threshold) or (mileage_depletion < min_mileage_threshold):
            print('Trip ', t, ' incomplete due to insufficient charge/mileage. Charge battery.')
            break
        else: 
            print('Trip ', t, ' complete!')
            bus.current_charge_pct = charge_depletion
            bus.mileage_remaining = mileage_depletion
            trips_complete += 1
            
    # plot charging/mileage profiles x trip 
    plt.plot(range(trips_complete), charging_profile)
    plt.title('Charging Profile')
    plt.xlabel('Number of Completed Trips')
    plt.ylabel('Charging %')
    
    plt.plot(range(trips_complete), mileage_profile)
    plt.title('Mileage Profile')
    plt.xlabel('Number of Completed Trips')
    plt.ylabel('Mileage')
    
    
    

### Run program

if __name__ == '__main__':
    
    # global vars -- TBD
    max_mileage = XXX # max mileage upon full charge
    start_charge_pct = XXX # max charge at start 
    min_charge_threshold = XXX # minimum allowed charge remaining
    min_mileage_threshold = XXX # minimum allowed mileage remaining 
    blockID = XXX # block of interest 
    datafilepath = '/Users/sumati/Documents/CMU/Academics/Spring2023/Capstone/code/data/'
    df = pd.read_csv(datafilepath+'trips_flattened_eastLibRoutes.csv')

    
    charge_status_via_trip_completion(df, blockID, start_charge_pct, max_mileage, 
                                      min_charge_threshold, min_mileage_threshold)
    




