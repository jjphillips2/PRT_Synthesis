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
        
    #Charges bus, takes in charger type of 'Faster' or 'Slower' for the 450kW or 150kW charger
    def chargeBus(self, chargeTime, start_charge_pct, charge=True, chargerType = 'Faster'):
        
        if(chargerType == 'Faster'):
            AddedCharge = chargeTime*60/35
        elif(chargerType == 'Slower'):
            AddedCharge = chargeTime*60/130
        else:
            print("charger type not charicterized in model")
        if(self.current_charge_pct + AddedCharge > start_charge_pct):
            AddedCharge = start_charge_pct - self.current_charge_pct
        if(charge):
            self.current_charge_pct = self.current_charge_pct + AddedCharge
        return AddedCharge
        
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
        self.trip_duration = None
        
# function to get the amount of charge required to complete a specified route--TBD       
def get_charge_required(distance_traveled, durationMinutes, time_of_year, eval_type):
    '''
    Parameters
    ----------
    distance_traveled : float
    time_of_year: str, takes values ("Winter", or "Summer")
    eval_type: 'reg' for regression or 'wc' for worst case scenario
    
    Purpose
    --------
    Takes the distance and seasonality and 
    calculates the battery charge required to complete that distance

    Returns
    -------
    float: battery percentage required to complete the specified route
    '''
    if time_of_year == 'Summer':
        if eval_type == 'reg':
            Distancebeta = 0.1799
            timeBeta = 0.0565
            const = 1.2035
        else: 
           beta = 0.8156
           const = 0
        
    else:
        if eval_type == 'reg':
            Distancebeta = 0.3257
            timeBeta = 0.0701
            const = -0.0178 
        else: 
            beta = .92
            const = 0
            
    #batteryChange = abs((beta*durationMinutes) + const)
    batteryChange = abs((Distancebeta*distance_traveled)+(timeBeta*durationMinutes)+const)
    return(batteryChange)
    
    


# function to conduct checks at the start of each trip for a block, flags when charging layover is needed
def charge_status_via_trip_completion(trips_flattened_df, blockID, start_charge_pct,
                                      min_charge_threshold, time_of_year, eval_type, min_charge_time, time_to_charge):
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
    eval_type: str, 'reg' or 'wc'
        whether to calculate charge depletion based on regression results or 
        worst case scenario analysis
    min_charge_time: int
        minimum number of minutes required for charge to happen. Usually flags a layover period
    
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
    last_end_time = 60*27 # there are some trips that continue into the next day, so the hour time stamps are > 24
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
        trip.trip_duration = trip_df.timeDelta_minutes.iloc[0]
        trip.charge_required = get_charge_required(trip.total_trip_distance,trip.trip_duration,
                                                   time_of_year, eval_type)
        
        
        #get time in minutes when the trip starts
        (h, m, s) = trip.start_time.split(':')
        start_time = int(h) * 60 + int(m) + int(s)/60
        #Find if there is enough time to charge bus
        if(start_time - last_end_time > min_charge_time):
            '''
            UPDATE: add location-based check to make sure charging happens at layover point 
                that can support charging
            UPDATE: make sure can complete the charge/travel to and from charging point 
                within the layover time
            FOR THIS WE NEED LIST OF LAYOVER LOCATIONS THAT ARE GOOD.
            '''
            #seeing what would happen if it were allowed to charge in layover
            #set charge to false for normal failures
            try:
                charge_time = start_time - last_end_time - 2*time_to_charge['time'].loc[trip.trip_id]
            except:
                charge_time = start_time - last_end_time
            if(charge_time > 0):
                #seeing what would happen if it were allowed to charge in layover
                #set charge to false for normal failures
                added_charge = bus.chargeBus(charge_time, start_charge_pct, charge=False)
            
        #find new end time current trip
        (h,m,s) = trip.end_time.split(':')
        last_end_time = int(h)*60 + int(m) + int(s)/60
        
        charge_depletion = bus.current_charge_pct - trip.charge_required 
        charging_profile.append(charge_depletion)
        
        # if remaining charge/mileage is insuffiecient, break and charge battery
        if charge_depletion < min_charge_threshold:
            print('Trip ', t, ' in block ', blockID, ' incomplete due to insufficient charge level. Charge battery.')
            return(t, blockID)
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
    
    
def get_charge_needed(df, blockID, start_charge_pct, min_charge_threshold, 
                      time_of_year, eval_type,time_to_charge):
    bus = Bus()
    bus.current_charge_pct = start_charge_pct
    bus.block_id = blockID
    
    # get trip list based on block_id
    trips = df[df.block_id == blockID].trip_id.tolist()
    
        
    # initialize dict which will contain time possible to charge during layover
    charge_options = {}
    last_end_time = 60*24
    # initialize array to keep track of charge for plotting charge depletion x trip 
    charge = start_charge_pct
    trips_complete = 1
    for i, t in enumerate(trips): 
        trip_df = df[(df.block_id == blockID) & (df.trip_id == t)]
        trip = Trip()
        trip.trip_id = t
        trip.route_id = trip_df.route_id.iloc[0]
        trip.start_time = trip_df.trip_start_time.iloc[0]
        trip.end_time = trip_df.trip_end_time.iloc[0]
        trip.trip_duration = trip_df.timeDelta_minutes.iloc[0]
        
        #get time in minutes when the trip starts
        (h, m, s) = trip.start_time.split(':')
        start_time = int(h) * 60 + int(m) + int(s)/60
        #Find if there is enough time to charge bus
        if(start_time - last_end_time > min_charge_time):
            #check to see if trip is at charge location
            try:
                charge_time = start_time - last_end_time - 2*time_to_charge['time'].loc[int(trip.trip_id)]
                print('checkpoint' + str(t))
                print('charge time', charge_time)
            except:
                #needed because currently don't have comprehensive list of all trips associated with layovers
                charge_time = start_time - last_end_time
            if(charge_time > 0):
                #seeing what would happen if it were allowed to charge in layover
                #set charge to false for normal failures
                added_charge = bus.chargeBus(charge_time, start_charge_pct, charge=False)
                charge_options.update({trip.trip_id: added_charge})
            
        #find new end time current trip
        (h,m,s) = trip.end_time.split(':')
        last_end_time = int(h)*60 + int(m) + int(s)/60
        
        trip.total_trip_distance = trip_df.total_distance_traveled.iloc[0]
        trip.charge_required = get_charge_required(trip.total_trip_distance, trip.trip_duration,
                                                   time_of_year, eval_type)           
        
        bus.current_charge_pct = bus.current_charge_pct - trip.charge_required 
        
    chargeNeeded = min_charge_threshold - bus.current_charge_pct
    return [chargeNeeded, charge_options]

### Run program

if __name__ == '__main__':
    
    # global vars
    start_charge_pct = 90 # max charge at start 
    min_charge_threshold = 30 # minimum allowed charge remaining
    min_charge_time = 5 #minimum charging time in minutes
    time_of_year = 'Winter' # seasonality var
    eval_type = 'reg' # whether to eval charging profile by regression or worst case scenario
    datafilepath = ''
    df = pd.read_csv(datafilepath+'trips_flattened_eastLibRoutes_miles.csv')

    allBlocks = np.unique(df.block_id)
    tripFails = []
    
    #example set of trips where charging is required
    tripLocations = [[1, [11806070, 9999070, 1775070, 11532070, 9943070]],
                      [2, [11297070, 4420070, 12721010, 6313010, 1376010, 11660010]],
                      [3, [10584010, 8609010]], [4, [5375080, 10799080, 6766080, 12005080, 9474080, 10788080]],
                      [5, [9832020, 5766020, 1385020, 4293020, 11142020, 7087020, 10114020]],
                      [6, [4787020, 9255020, 4367020, 7779020, 6236020, 5849020, 9728020]]]
    #whether charging location has charger or not, 1 for charger, 0 no charger
    charge_locations = [1, 0 , 0, 1, 0, 1]
    #how long does it take to get from layover needing charge to potential charger location
    travel_time_matrix = pd.read_csv('TraveltoChargerMatrix.csv', dtype=int)
    #convert the above three data structures to list of route number and time it takes to get to active charger
    time_to_charge = []
    for item in tripLocations:
        for i in range(len(item[1])):
            if(charge_locations[item[0]-1] == 1):
                time_to_charge.append([item[1][i],item[0], 0])
            else:
                best_time = 60
                best_location = 0
                for j in range(len(travel_time_matrix[str(item[0])])):
                    if(charge_locations[j] == 1):
                        if(travel_time_matrix[str(item[0])].iloc[j] < best_time):
                            best_time = travel_time_matrix[str(item[0])].iloc[j]
                            best_location = j
                time_to_charge.append([item[1][i], best_location, best_time])
    time_to_charge = pd.DataFrame(time_to_charge, columns=['trip','location', 'time'])
    time_to_charge.set_index('trip', inplace=True)
    
    blockID_needing_charge = []
    block_charge_options = []
    for block in allBlocks:
        blockCheck = charge_status_via_trip_completion(df, block, start_charge_pct, 
                                      min_charge_threshold, time_of_year, eval_type, 
                                      min_charge_time, time_to_charge)
        
        if blockCheck != None:
            tripFails.append(blockCheck[0])
            blockID_needing_charge.append(blockCheck[1])
            
    tripFails = [i for i in tripFails if i != None]
    blockID_needing_charge = [i for i in blockID_needing_charge if i != None]
    print(tripFails)
    print()
    print('Failed in '+ str(len(tripFails)) + ' blocks in ' + time_of_year)
    
    df[df.block_id.apply(lambda x: x in blockID_needing_charge)].to_csv('blocks_needing_charge.csv')
    
   
    
    #Finds how much charge the failed blocks need to be sucessful, need to set charge in bus charging to False to work properly
    charge_needed_list = []
    for block in blockID_needing_charge:
        FailedBlockCheck = get_charge_needed(df, block, start_charge_pct,
                                               min_charge_threshold, time_of_year, eval_type,
                                               time_to_charge)
        charge_needed_list.append([block, FailedBlockCheck[0]])
        block_charge_options.append([block, FailedBlockCheck[1]])
        
   

    

    
    


