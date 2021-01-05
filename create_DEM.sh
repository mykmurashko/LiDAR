for year in 2018n
do 
	echo $year

	DSM=DSM@1/DSM$year.tif
	DTM=DTM/DTM_CONSTANT.tif

	extents=`python3 getrasterextents.py $DSM`
	echo "extents of $year are $extents"

	#clip the DTM to the boundaries of the DSMc
	gdal_translate -projwin $extents -of GTiff $DTM DTM$year.tif

	#DEM=DTM-DSM
	gdal_calc.py -A $DSM  -B DTM$year.tif --outfile=DEM/DEM$year.tif --calc="A-B"

	#remove temporary files
	rm DTM$year.tif
done