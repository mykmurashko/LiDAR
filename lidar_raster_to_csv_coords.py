from raster2xyz.raster2xyz import Raster2xyz
import pandas as pd

def main():
	input_raster = "input.tif"
	out_csv = "output.csv"
	rtxyz = Raster2xyz()
	rtxyz.translate(input_raster, out_csv)

	df=pd.read_csv(out_csv)
	print(df.head(5))
	print(df.columns)

	df.loc[df['z'] < 3, 'z'] = 0
	df.loc[df['z'] > 200, 'z'] = 0
	print(df.head(20))
	minx=min(df.x)
	print(minx)
	miny=min(df.y)
	df['x']=df['x']-minx
	df['y']=df['y']-miny
	print(df.head(20))
	df.to_csv(out_csv, index=False, header=False)

if __name__=='__main__':
	main()
