import gdal
from gdalconst import GA_ReadOnly
import sys, os

path="/Users/mykolamurashko/Documents/DISSERTATION/Longitudonal study/delta volumes from DSMs/dem constant dtm/"

arg1=sys.argv[1]

FILE=os.path.join(path+arg1)

data = gdal.Open(FILE, GA_ReadOnly)
geoTransform = data.GetGeoTransform()
minx = geoTransform[0]
maxy = geoTransform[3]
maxx = minx + geoTransform[1] * data.RasterXSize
miny = maxy + geoTransform[5] * data.RasterYSize
print(minx, maxy, maxx, miny)