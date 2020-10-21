# LiDAR
Methodology for extracting built up volumes from areal LiDAR scans

The following was used to extract data on built up volumes in the 649 wards of London from Digital Elevation Models. 
Please refer to the DEM_creation file for instructions on how to efficiently calculate DEMs from surface scans and terain information.

The pull_stats file pulls zonal statistics from the LiDAR scans. I was particularly interested in Volumes, Building Footprint and Total Coverege of the scan. 
I worked with DEMs at a 1m resolution, please note that you will have to tweak the volumes/footprint/coverage defintions if the resolution of your scans is different. 

The data_wrangle file cleans this data - 
1) removes wards that were only partially scanned from the dataset
2) plots a map showing the frequency with which each ward has been covered by the data
3) calculates averege year on year built volumes growth rate for that ward
4) plots this data 

