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
            Distancebeta = -0.42933544
            timeBeta = 0
            const = -1.91616128
        else: 
           beta = 0.8156
           const = 0
        
    else:
        if eval_type == 'reg':
            Distancebeta = -0.5902
            timeBeta = 0
            const = -1.7664
        else: 
            beta = .92
            const = 0
            
    #batteryChange = abs((beta*distance_traveled) + const)
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
            if(charge_time > min_charge_time):
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
            
    
    '''
    # plot charging profiles x trip 
    plt.scatter(range(trips_complete), charging_profile)
    plt.plot(range(trips_complete), charging_profile)
    plt.title('Charging Profile')
    plt.xlabel('Number of Completed Trips')
    plt.ylabel('Charging %')
    plt.xticks(range(15))
    '''
    
    
def get_charge_needed(df, blockID, start_charge_pct, min_charge_threshold, 
                      time_of_year, eval_type,time_to_charge, min_charge_time, numberOchargers):
    bus = Bus()
    bus.current_charge_pct = start_charge_pct
    bus.block_id = blockID
    charge_locations = []
    # get trip list based on block_id
    trips = df[df.block_id == blockID].trip_id.tolist()
    ChargePoints = ''
        
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
            except:
                #needed because currently don't have comprehensive list of all trips associated with layovers
                charge_time = 0
            if(charge_time > min_charge_time):
                #seeing what would happen if it were allowed to charge in layover
                #set charge to false for normal failures
                added_charge = bus.chargeBus(charge_time, start_charge_pct, charge=True)
                numberOchargers.loc[time_to_charge['location'].loc[t]] 
                
                if(time_to_charge['location'].loc[trip.trip_id] in charge_options):
                    charge_options[time_to_charge['location'].loc[trip.trip_id]] += added_charge
                else:
                    charge_options.update({time_to_charge['location'].loc[trip.trip_id]: added_charge})
                ChargePoints = ChargePoints + ',' + str(t)
            
        #find new end time current trip
        (h,m,s) = trip.end_time.split(':')
        last_end_time = int(h)*60 + int(m) + int(s)/60
        
        trip.total_trip_distance = trip_df.total_distance_traveled.iloc[0]
        trip.charge_required = get_charge_required(trip.total_trip_distance, trip.trip_duration,
                                                   time_of_year, eval_type)           
        
        bus.current_charge_pct = bus.current_charge_pct - trip.charge_required 
        
    chargeNeeded = min_charge_threshold - bus.current_charge_pct
    if(chargeNeeded < 0):
        chargeNeeded = 0
    return [chargeNeeded, charge_options, ChargePoints]

### Run program

if __name__ == '__main__':
    
    # global vars
    start_charge_pct = 90 # max charge at start 
    min_charge_threshold = 30 # minimum allowed charge remaining
    min_charge_time = 5 #minimum charging time in minutes
    time_of_year = 'Winter' # seasonality var
    eval_type = 'reg' # whether to eval charging profile by regression or worst case scenario
    datafilepath = ''
    df = pd.read_csv(datafilepath+'trips_flattened_allRoutes.csv')

    allBlocks = np.unique(df.block_id)
    tripFails = []
    time_to_charge = pd.read_csv('time_to_charge.csv')
    time_to_charge = time_to_charge.set_index('trip')
    
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
    
    df[df.block_id.apply(lambda x: x in blockID_needing_charge)].to_csv('blocks_needing_charge.csv')
    print('\nNumber of failed blocks: ', len(blockID_needing_charge))
    
    
    numberOchargers = pd.DataFrame({'stop_id': [4405, 8308,16063,22873,16111,8812,19687,15276,22326,3302,21624,1407],
                                    'charger': [np.zeros(3600*24),
                                                np.zeros(3600*24),
                                                np.zeros(3600*24),
                                                np.zeros(3600*24),
                                                np.zeros(3600*24),
                                                np.zeros(3600*24),
                                                np.zeros(3600*24),
                                                np.zeros(3600*24),
                                                np.zeros(3600*24),
                                                np.zeros(3600*24),
                                                np.zeros(3600*24),
                                                np.zeros(3600*24),]})
    numberOchargers = numberOchargers.set_index('stop_id')
    
    #example set of trips where charging is required
    tripLocations = pd.DataFrame({'stop_id': [4405, 8308,16063,22873,16111,8812,19687,15276,22326,3302,21624,1407], 
                                  'trips': [[12934070, 11671070, 2147070, 4280070, 9717070, 5465070, 7108070, 12062070, 613070, 6971070, 10596070, 5929070, 8986070, 2315070, 7272070, 10979070, 1160070, 5044070, 9669010, 2904010, 3606010, 13009010, 6219010, 3896010, 9345010, 3267010, 4519010, 3837010, 5055010, 5281010, 9702080, 696080, 13087080, 10660080, 13170080, 7350080, 4792080, 11216080, 9806080, 3399080, 7514080, 7202080, 11340020, 871020, 9247020, 2803020, 2982020, 4265020, 7578020, 2079020, 7619020, 5045020, 3671020, 2114020],
                                  [7906070, 11698070, 8893070, 7707070, 5179070, 4015070, 7834070, 6738070, 5626070, 10092010, 1615010, 10173010, 6134010, 13733010, 13702010, 2470080, 8600080, 6516080, 7512080, 4309080, 6973080, 12541020, 12926020, 5583020, 7079020, 6151020, 4424020],
 [7800070, 5975070, 5213070, 1966070, 4054070, 11729070, 7521070, 4206070, 4665070, 12976070, 12821070, 8618070, 7686070, 6793070, 1324070, 1725070, 5299070, 2156070, 4872070, 10113070, 1377070, 7563070, 3264070, 13502070, 12806070, 12786070, 5220070, 8728070, 6359070, 2313070, 13411070, 6279070, 7339070, 1368070, 2553070, 379070, 4242070, 1745070, 5909070, 5241070, 12419070, 7544070, 12178070, 6967070, 7231070, 5616070, 3948070, 3825070, 3890070, 13370070, 11829070, 2393070, 1355070, 969070, 4634010, 10145010, 13864010, 1183010, 5163010, 3579010, 6154010, 13185010, 10460010, 455010, 2924010, 14005010, 5982010, 8625010, 2201010, 1271010, 13731010, 4283010, 11479010, 7809010, 14057010, 9069010, 2213010, 9083010, 11612010, 7682010, 2395010, 8373010, 3428010, 8807010, 7182010, 8817010, 771010, 7102010, 13675010, 7408010, 11460010, 5662010, 1848010, 7704010, 12743010, 4059010, 3941080, 5285080, 6084080, 14031080, 6338080, 13116080, 1293080, 12851080, 2858080, 2901080, 2064080, 7712080, 506080, 13140080, 12080, 11526080, 1239080, 13269080, 12033080, 11421080, 3908080, 4722080, 131080, 3001080, 10659080, 12667080, 9529080, 11779080, 3004080, 3299080, 2146080, 4040080, 7789080, 8495080, 4050080, 4633080, 11769080, 3790080, 6422080, 35080, 9135080, 8249080, 5959020, 13221020, 3443020, 10454020, 9746020, 12028020, 1828020, 4322020, 3065020, 5762020, 4787020, 1557020, 12576020, 6982020, 598020, 452020, 7392020, 8717020, 3020, 12456020, 9255020, 2655020, 2085020, 1996020, 12388020, 12828020, 68020, 5438020, 2369020, 4367020, 12859020, 9676020, 9464020, 11908020, 10025020, 13887020, 908020, 4187020, 1568020, 1906020, 7849020, 8276020, 7779020, 5492020, 11930020, 5597020, 1275020, 12219020, 5072020, 7545020, 5879020, 4205020, 5126020, 10684020, 11914020, 1802020, 11232020, 6236020, 2140020, 11423020, 5093020, 8993020, 638020, 7889020, 5385020, 5849020, 7074020],
 [1493070, 12009070, 5030070, 8687070, 1914070, 8210070, 1118070, 2077070, 8682070, 8791070, 9571070, 7376070, 5846070, 2992070, 4387010, 3627010, 397010, 758010, 2015010, 3324010, 5638010, 4260010, 12244010, 7250010, 578010, 4375010, 2883010, 1850010, 1586080, 8710080, 4395080, 4303080, 6899080, 2183080, 10419080, 1401080, 4365080, 2529080, 4074080, 2909080, 1628080, 353080, 4123020, 1385020, 5426020, 5877020, 4293020, 9414020, 13962020, 11343020, 3727020, 2051020, 7333020, 10248020, 1128020, 10114020, 1590020, 1009020, 6675020],
 [9383070],
 [600070],
 [14019070, 8227070, 10664070],
 [10669070, 216070, 1335070, 9111070, 7763070, 7677070, 8344070, 8723070, 3078070, 1235070, 12416070, 6833070, 14058070, 9643070, 9628070, 8060070],
 [11662020, 2591020, 3856020, 7650020, 5766020, 5404020, 5865020, 4087020],
 [9832020, 4960020],
 [7219020, 11618020],
 [1489020, 5076020]]})
    tripLocations = tripLocations.set_index('stop_id')
    #whether charging location has charger or not, 1 for charger, 0 no charger
    charge_locations = [1, 0 , 1, 1, 0, 0,1,1,1,0,0,0]
    #how long does it take to get from layover needing charge to potential charger location
    travel_time_matrix = pd.read_csv('TraveltoChargerMatrix.csv', dtype=int)
    travel_time_matrix = travel_time_matrix.set_index('index')
    #convert the above three data structures to list of route number and time it takes to get to active charger
    time_to_charge = []
    for k in range(len(tripLocations)):
        item = tripLocations['trips'].iloc[k]
        stop = tripLocations.index.values[k]
        for i in item:
            if(charge_locations[k] == 1):
                time_to_charge.append([i, stop, 0])
            else:
                best_time = 60
                best_location = stop
                for j in range(len(travel_time_matrix)):
                    if(charge_locations[j] == 1):
                        if((travel_time_matrix[str(stop)].iloc[j]) < best_time):
                            best_time = travel_time_matrix[str(stop)].iloc[j]
                            best_location = travel_time_matrix.index.values[j]
                time_to_charge.append([i, best_location, best_time])
    time_to_charge = pd.DataFrame(time_to_charge, columns=['trip','location', 'time'])
    time_to_charge.set_index('trip', inplace=True)
    
    
    #Finds how much charge the failed blocks need to be sucessful, need to set charge in bus charging to False to work properly
    charge_needed_list = []
    ChargePoints = ''
    for block in blockID_needing_charge:
        FailedBlockCheck = get_charge_needed(df, block, start_charge_pct,
                                               min_charge_threshold, time_of_year, eval_type,
                                               time_to_charge, min_charge_time, numberOchargers)
        charge_needed_list.append([block, FailedBlockCheck[0]])
        block_charge_options.append([block, FailedBlockCheck[1]])
        ChargePoints = ChargePoints + ',' + FailedBlockCheck[2]
    
    
    df = df.set_index('trip_id')
    ChargePoints = ChargePoints.split(',')
    tripLocations = pd.Series(dtype=float)
    for i in ChargePoints:
        if i != '':
            i = int(i)
            stop = df['start_stop_id'].loc[i]
            if stop in tripLocations:
                tripLocations.loc[stop].append(i)
            else:
                tripLocations.loc[stop] = [i]
    
    tripLocations.to_csv('LayoverLocNeedCharge.csv')
    time_to_charge.to_csv('time_to_charge.csv')

    
    


