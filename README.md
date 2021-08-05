# LiDAR

TL;DR: Method for calculating building volumes and new construction volumes from lidar:
1. create_DEM.sh is a bash file which uses GDAL to clean lidar data and export the DEM. (read manual for dem creation)
2. calculate_zonal_stats.py calculates zonal stats (volume, footprint, coverage) from DEM.

To visualise dem in 3d we do two things:

1. translate raster into a csv with cartesian coordinates centred at 0,0,0 using lidar_raster_to_csv_coords.py      
2. use grasshopper in rhino to create a delenauay mesh between those coordinates: visalise_in_3d.gh


___________________________________________________

We use Light Detection and Ranging (LiDAR) in order to quantify the physical form of London. LiDAR is a method for measuring the distance to a target by illuminating it with a laser and recording the time it takes for the reflection to return. First introduced in 1961 to track satellites, by 1971, it was used to map the surface of the moon as part of the Apollo 15 mission. Thanks to the rate of technological progress, we are able to use the same technology as the astronauts in order to measure the built form of London.

This has been made possible by the Environment Agency (EA), which has been putting LiDAR on its aircraft since 1998. The agency uses elevation profiles of the country for flood risk mapping. The airborne LiDAR scanners output a point-cloud: a set of coordinates that correspond to the individual laser returns. These measurements are used to construct raster representations of the surface.


The EA constructs two types of such representations: first, Digital Surface Models (DSM) record the elevation of the city’s surface; second, Digital Terrain Models (DTM) estimate the profile of the ground alone. (This data has been timestamped and made available to the public through the DEFRA portal https://environment.data.gov.uk/DefraDataDownload/?Mode=survey.
) The EA evaluates the absolute height error of this data to be less that +-15cm. This accuracy is more than high enough to reliably measure built form (EA, 2012).
 
In the context of Greater London, scans date back to 1999. Since then, all of the city has been scanned at least once at a spatial resolution accurate to at least 1 meter. Approximately 70% of London has been scanned more than once, allowing us to track changes in development.
![frequency_of_coverage](https://user-images.githubusercontent.com/73239125/128371302-7eb7ff3c-41be-4cc8-9cda-c39b7c8028d6.png)

In order to measure built form, we calculate **Digital Elevation Models**: representations of the buildings and structures above ground. To do this we subtract the terrain (DTM) from the surface (DSM):

<img width="155" alt="image" src="https://user-images.githubusercontent.com/73239125/128371452-97de1db0-6980-4665-aba7-9e4516b6dbfb.png">

Whereas DSMs are a product of simple aggregation of point cloud data, DTMs are calculated via interpolation. As a result, the margin of error in the DTMs is higher. In order to avoid random variation in the Terrain Models from introducing noise into the data, we assume that the terrain in London has stayed constant over the last 20 years. A single terrain model is used in the calculation of elevation models for all the observed time periods.


The resulting elevation models capture all objects above the ground. We are interested specifically in the buildings. Whereas cars and pedestrians do not feature in the scans, trees feature prominently. We erase trees from the model by relying on the GLA’s Green and Blue cover dataset2, which combines land use data with near-infrared aerial imagery (NDVI) to arrive at a geo-spatial record which maps every tree, river, lake and pond in Greater London. We evaluate all natural artefacts to zero. The process of creating DEMs relies on the Geospatial Data Abstraction Library 3 and was automated using the bash programming language (first file).


We extract zonal statistics for built up volumes and building footprints from DEMs. This is done by performing simple arithmetic on the elevation values of cells that fall within the boundary of a given zone. A hypothetical case is described bellow:
<img width="580" alt="image" src="https://user-images.githubusercontent.com/73239125/128372387-2ada1c1b-c422-43bd-9fbb-df283bb42d2d.png">


This process was automated using the python coding language and in part relies on open source code in the rasterstats package ( https://pythonhosted.org/rasterstats/rasterstats.html). The python file in the repo contains the function calculate zonal stats which calculates the following zonal statistics:
1. Coverage(m2): a record of the area that was covered by the LiDAR scan within a zone. Some zones fall partially outside the area covered by a given scan. Coverage allows us to compare the area covered by the scan with the true zonal area and discard subsequent statistics if the coverage is partial. (lines 17-23)
2. Footprint(m2): a record of the footprint of buildings in the zone. Since we have ’cleaned’ the DEM of natural features, we assume that all cells with elevations greater than 2 meters are buildings. Footprint is a count of the number of values inside the zone which have a height greater than 2 meters (line 26).
3. Volume(m3): a record of the built up volume in the zone. We sum the heights of all cells greater than 2 meters (line 30).


