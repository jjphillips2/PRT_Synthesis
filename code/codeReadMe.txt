ReadMe for the Code Files 

BusMileage.py: main program for simulation. Finds block failures, potential layover spots, and assesses impact of chargers at points of failure

baselineLinearModel.py: exploratory linear model, used at midpoint. See PRT_Model.ipynb for final modeling results 

create_trips_flattened.py: create the flattened trips dataset using the trips, stops, and stop times GTFS datasets. Merges those three datasets together, and re-structures the data to be at the trip-id level. Input dataset for simulation code in  BusMileage.py. 

endStop_layover_distances.py: code to calculate driving distances from flagged end stops to potential layover locations using the Google API. Creates a distance matrix. 

getLastRoutes.py: code to run after BusMileage.py to identify the nearest layover stop before the failed trip within the failed block. Summarizes the common routes associated with failed blocks. 

Model_PRT.ipynb: Code for linear regression models for charge depletion estimation. 

prt_coordinates.ipynb: code to calculate driving distances using Google API


