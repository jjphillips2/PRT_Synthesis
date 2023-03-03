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
        - charge required
    
    """
    def __init__(self):
        self.trip_id = None
        self.route_id = None
        self.start_time = None
        self.end_time = None
        self.total_trip_distance = None
        self.charge_required = None
        
# function to get the amount of charge required to complete a specified route--TBD       
def get_charge_required(distance_traveled, time_of_year):
    '''
    Parameters
    ----------
    distance_traveled : float
    time_of_year: str, takes values ("Winter", or "Summer")
    
    Purpose
    --------
    Takes the distance and seasonality and 
    calculates the battery charge required to complete that distance

    Returns
    -------
    float: battery percentage required to complete the specified route
    '''
    if(time_of_year == 'Summer'):
        beta = -.42933544
        const = -1.91616128
        
    else:
        beta = .92
        const = 0
        
    batteryChange = abs((beta*distance_traveled) + const)
    return(batteryChange)
    
    


# function to conduct checks at the start of each trip for a block, flags when charging layover is needed
def charge_status_via_trip_completion(trips_flattened_df, blockID, start_charge_pct,
                                      min_charge_threshold, time_of_year):
    '''
    Parameters
    ----------
    trips_flattened_df : dataframe
        output of the create_trips_flattened.py file, block-trip level dataset on the drive.
    blockID : float
        global var, block ID of interest.
    start_charge_pct : float
        global var, charging pct of bus at "full charge"
    min_charge_threshold : float
        global var, min allowed charge for bus to take a trip.
    time_of_year: int, indicator var
        whether it is a summer or winter time of year, global var
    
        
    Purpose
    --------
    For each trip in a block, assess whether bus can complete trip before hitting minimum
    threshold for charge. Identifies when charging layovers should be complete. 
    Assumes within-trip charging not allowed. 

    Returns
    -------
    Prints whether bus can complete a trip, and at what point to have a charging layover.
    Prints line graph of charging profile x trip.

    '''
    # initialize bus parameters
    bus = Bus()
    bus.current_charge_pct = start_charge_pct
    bus.block_id = blockID
    
    # get trip list based on block_id
    trips = trips_flattened_df[trips_flattened_df.block_id == blockID].trip_id.tolist()
    
    # initialize array to keep track of charge for plotting charge depletion x trip 
    charging_profile = [start_charge_pct]
    
    
    # for each trip in the specified block, store the relevant attributes, and check whether remaining charge/mileage is sufficient to complete next trip
    trips_complete = 1
    for i, t in enumerate(trips): 
        trip_df = trips_flattened_df[(trips_flattened_df.block_id == blockID) & 
                                     (trips_flattened_df.trip_id == t)]
        trip = Trip()
        trip.trip_id = t
        trip.route_id = trip_df.route_id.iloc[0]
        trip.start_time = trip_df.trip_start_time.iloc[0]
        trip.end_time = trip_df.trip_end_time.iloc[0]
        trip.total_trip_distance = trip_df.total_distance_traveled.iloc[0]
        trip.charge_required = get_charge_required(trip.total_trip_distance, time_of_year)
        
        charge_depletion = bus.current_charge_pct - trip.charge_required 
        
        charging_profile.append(charge_depletion)
        
        
        # if remaining charge/mileage is insuffiecient, break and charge battery
        if charge_depletion < min_charge_threshold:
            print('Trip ', t, ' in block ', blockID, ' incomplete due to insufficient charge level. Charge battery.')
            return(t)
            break
        else: 
            #print('Trip ', t, ' complete!')
            bus.current_charge_pct = charge_depletion
            trips_complete += 1
    
    
    # plot charging profiles x trip 
    plt.scatter(range(trips_complete), charging_profile)
    plt.plot(range(trips_complete), charging_profile)
    plt.title('Charging Profile')
    plt.xlabel('Number of Completed Trips')
    plt.ylabel('Charging %')
    plt.xticks(range(15))
    
#Charges bus, takes in Bus object, charger type of 'Faster' or 'Slower' for the 450kW or 150kW charger
def chargeBus(Bus, chargeTime, start_charge_pct, chargerType = 'Faster'):
    if(chargerType == 'Faster'):
        AddedCharge = chargeTime*60/35
    elif(chargerType == 'Slower'):
        AddedCharge = chargeTime*60/130
    else:
        print("charger type not charicterized in model")
    Bus.current_charge_pct = Bus.current_charge_pct + AddedCharge
    if(Bus.current_charge_pct > start_charge_pct):
        Bus.current_charge_pct = start_charge_pct    

### Run program

if __name__ == '__main__':
    
    # global vars -- TBD
    start_charge_pct = 90 # max charge at start 
    min_charge_threshold = 30 # minimum allowed charge remaining
    #blockID =  183315607 # block of interest 
    time_of_year = 'Winter' # seasonality var
    datafilepath = ''
    df = pd.read_csv(datafilepath+'trips_flattened_eastLibRoutes_miles.csv')

    allBlocks = np.unique(df.block_id)
    tripFails = []
    for block in allBlocks:
        tripFails.append(charge_status_via_trip_completion(df, block, start_charge_pct, 
                                      min_charge_threshold, time_of_year))
        
    tripFails = [i for i in tripFails if i != None]
    print(tripFails)
    print()
    print('Failed in '+ str(len(tripFails)) + ' blocks in ' + time_of_year)
    
    



