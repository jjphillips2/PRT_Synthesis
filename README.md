# Pittsburgh Regional Transit: Strategy for Fleet Electrification
## Pittsburgh Regional Transit x Carnegie Mellon University
#### Last Updated: May 2023

As green infrastructure advances, cities are exploring innovative approaches to decrease carbon emissions. Pittsburgh is no exception, and Pittsburgh Regional Transit (PRT) is taking the lead with the goal to convert its entire bus fleet to 100% electric vehicles by 2045. The organization has pledged to make significant reductions in carbon emissions over the next decade and has already started purchasing fully electric buses. Although most buses are still gas-powered or hybrid, a few routes are now serviced by electric buses. PRT is planning to install charging stations to enable the deployment of additional electric buses throughout the system. 

Given the nature of battery electric buses, these buses are likely to need charge at some point in their route. The problem presented to the team was to understand the optimal locations to place these chargers given a variety of factors. To address the problem, a number of tools were utilized, including Python, ArcGIS, cost/benefit analyses and binary optimization modeling. A linear regression model was created based on past PRT test data of electric buses to understand the average battery depletion over time. From there, a Python script was developed to assess all routes within the PRT system and the potential charge depletion along each route over time. This helped to identify routes that were at risk of failure across the system, and subsequently where charging locations might need to be installed. Viable charging locations were assessed using a variety of other metrics including land parcel size, ownership and ability to serve other bus routes. This report will provide recommendations regarding structural capabilities, cost considerations, and community impact for the installation of charging stations in specific locations. 

This repository houses code files and data generated during our analyses that informed our results. See below for brief descriptions of the different folders: 
* allRoutes: folder with the results of running the simulation on all routes in the PRT system (assuming 40-ft buses) 
* brt: folder with the results of running the simulation on projected BRT routes
* code: folder housing key scripts and programs utilized for analysis. Contains a code-specific readMe for reference. 
* dataGenerated: contains files that are either outputs of the programs, or processed versions of files provided by PRT 
* eastLib: folder with results of running the simulation on routes from the East Liberty garage (assuming 40-ft buses)
* Map Bibliography/Methodology: resources/documentation for the supporting ArcGIS/Esri products delivered
* PRT_CMU_EBus.zip: data and ArcGIS files for supporting Esri products delivered
