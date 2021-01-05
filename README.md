# LiDAR

This is a work in progress, please email mm2331@cam.ac.uk with any queries

Methodology for extracting built up volumes from areal LiDAR scans

The following was used to extract zonal statistics on built up volumes in London from timestamped LiDAR data provided by the UK Environemnt Agency.

##Step 1: 
Digital Elevation Model Creation:
  The GDAL library is used for this step.
  Reffer to the 'Manual for DEM creation' for a brief walkthrough of the process
  Create_DEM.sh is a bash file that uses GDAL commands to create elevation models.

##Step 2:
Generate zonal statistics from timestamped files.
Get_Stats.py takes in a raster file and a georefferenced polygon as inputs. 
It calculates the zonal statistics for the data inside the polygon. It outputs this as a dict.

##Step 3: 
Visualise the changes in Volume for a specific zone:
Visualise_Lidar.py takes in a user input for the name of a Zone that the user wants to inspect.
It proceeds to find all scans that cover this zone. 
It outputs 3 items:
 
1. A .xlsx file with the zonal statistics for each of the years
2. A graph mapping the built up volume against time with a line of best fit through these points
3. A gif visualising the changes in the elevation profile for the zone
  
 

