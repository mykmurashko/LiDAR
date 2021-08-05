'''
calculate_zonal_stats returns the volume and footprint of buildings in a zone. The function takes 2 inputs:
    dem = path to the Digital Elevation Model stored as a .tif raster
    zone = shapely.geometry.polygon object corresponding to a zone boundary
'''

import shapely, rasterio
import numpy as np
from rasterstats import zonal_stats

def calculate_zonal_stats(dem, zone_polygon):
    resolution = rasterio.open(dem).res[0]
    true_area=zone_polygon.area
    stats = zonal_stats(zone_polygon, dem, stats=["count"],
                        add_stats={"volume": vol, "footprint": foot})
    # we express our zonal statistics in m^2 by multiplying them by the square of the resolution
    coverage = stats[0]['count'] * resolution * resolution 
    # output zonal statistics if the zone is covered fully, otherwise output NaN
    if coverage>(0.95*true_area):
        volume = stats[0]['volume'] * resolution * resolution 
        footprint = stats[0]['footprint'] * resolution * resolution 
    else:
        volume = footprint = np.nan
    return volume, footprint

def foot(x):
    # Count number of raster cells with an elevation higher than 2m
    return (np.sum(x > 2))

def vol(x):
    # Sum of all elevations greater than 2m
    return np.sum((x > 2) * x)