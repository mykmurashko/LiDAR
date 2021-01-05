import os.path
from matplotlib import pyplot
import matplotlib.pyplot as plt
from rasterstats import zonal_stats
import fiona
import rasterio
import rasterio.mask
import geopandas as gpd
import shapely
import numpy as np
import pandas as pd
import imageio

# directory in which we look for files to visualise:
root = '/Volumes/RED T7 MYK/Dissertation Lidar'
file_type = 'DEM'
msoa_shapefile = '/Users/mykolamurashko/Documents/DISSERTATION/Longitudonal study/MSOA 2011/MSOA_2011_London_gen_MHW.shp'
years = list(range(2003, 2020))
THRESHOLD = 0.9


def main():
    # clear contents of temp folder (clipped rasters, shapefile)
    delete_temp_contents()
    # get msoa from user, pull corresponding polygon from shapefile
    msoa, boundary_path = get_msoa_boundary()
    # create new folder for output files
    directory = create_new_folder(msoa)
    # get zonal statistics for every year
    df = create_empty_df()
    for year in years:
        # check whether raster exhists for given year. If 2 scans, take the one with heigher coverage
        raster_path = get_raster(year, boundary_path)
        if raster_path:
            df.loc[year, "File_Path"] = raster_path
            df = pull_zonal_stats(df, raster_path, boundary_path, year)
    df.to_excel(f"{directory}/df_{msoa}.xlsx")
    # remove values which cover less than THRESHOLD% of the max coverage for that msoa
    df = remove_partial_scans(df)
    # calculate growth in volumes
    growth = calculate_growth(df, msoa)
    # keep only years which have full scans
    df_condensed = df[df['Volume'] > 0]
    # output msoa-clipped DEM for each of the years in df_condensed
    pngs = []
    for index, row in df_condensed.iterrows():
        raster_path = df.loc[(index), "File_Path"]
        print(f"in {index} the path is {raster_path}")
        temp_raster = crop_raster(raster_path, boundary_path, index)
        png = show_2D(temp_raster, index, msoa, growth)
        #append list
        pngs = pngs + [png]
    make_gif(pngs, msoa)


def get_raster_path(year, resolution):
    if resolution == 0.5:
        folder = "Lidar at 50cm"
    elif resolution == 1:
        folder = "Lidar at 1m"
    path = str(root) + "/" + str(folder) + "/DEM/DEM" + str(year) + ".tif"
    return path


def get_msoa_boundary():
    msoa = ""
    gdf = gpd.read_file(msoa_shapefile)
    gdf = gdf.set_index('MSOA11NM')
    index = gdf.index
    while msoa not in index:
        msoa = str(input("MSOA: "))
    temp_df = gdf.filter(like=msoa, axis=0)

    geo = temp_df.at[msoa, 'geometry']
    if type(geo) == shapely.geometry.multipolygon.MultiPolygon:
        geo = max(geo, key=lambda a: a.area)
        temp_df.at[msoa, 'geometry'] = geo

    msoa_path = "/Users/mykolamurashko/Documents/DISSERTATION/Longitudonal study/visualise_lidar/Temp/temp_boundary.shp"
    temp_df.to_file(msoa_path)
    return msoa, msoa_path


def get_resolution(raster_file):
    file = rasterio.open(raster_file)
    reso = file.res[0]
    return reso


def coverage(file, boundary):
    reso = get_resolution(file)
    stats = zonal_stats(boundary, file, stats=["count"])
    count = stats[0]['count']
    count = count * (reso * reso)
    return count


def get_raster(year, msoa_path):
    resolutions = [0.5, 1]
    paths = []
    for resolution in resolutions:
        path = get_raster_path(year, resolution)
        if os.path.isfile(path):
            paths = paths + [path]
    if len(paths) == 1:
        raster = paths[0]
        print(f"{year}: there is 1 scan available")
        return raster
    elif len(paths) == 2:
        # if two scans, take the one with the higher coverage
        counts = []
        for raster_file in paths:
            count = coverage(raster_file, msoa_path)
            counts = counts + [count]

        mask = list(counts == np.max(counts))
        paths = np.array(paths)
        raster = paths[mask][0]
        reso = get_resolution(raster)
        print(
            f"{year}: there are 2 scans: at 0.5m the coverage is " + str(counts[0]) + ", at 1m the coverage is " + str(
                counts[1]) + f". So the {reso} scan will be used.")
        return raster
    else:
        pass
        print(f"{year}: there are no scans")


def create_empty_df():
    l = len(years)
    empty = [np.nan] * l
    empty_str = [""] * l
    data = {'Volume': empty,
            'Coverage': empty,
            'Footprint': empty,
            'File_Path': empty_str}
    # Creates pandas DataFrame.
    df = pd.DataFrame(data, index=years)
    return (df)


def volume(x):
    return np.sum((x > 3) * x)


def footprint(x):
    return (np.sum(x > 3))


def pull_zonal_stats(dataframe, raster_file_path, msoa_file_path, year):
    reso = get_resolution(raster_file_path)
    stats = zonal_stats(msoa_file_path, raster_file_path, stats=["count"],
                        add_stats={"Volume": volume, "Footprint": footprint})
    vol = stats[0]['Volume'] * reso * reso
    cov = stats[0]['count'] * reso * reso
    foot = stats[0]['Footprint'] * reso * reso

    dataframe.loc[year, "Volume"] = vol
    dataframe.loc[year, "Coverage"] = cov
    dataframe.loc[year, "Footprint"] = foot

    return dataframe


def remove_partial_scans(dataframe):
    max = np.nanmax(dataframe['Coverage'])
    culled = []
    for year in years:
        if dataframe.loc[(year), "Coverage"] < THRESHOLD * max:
            dataframe.loc[(year), 'Volume'] = np.nan
            dataframe.loc[(year), 'Footprint'] = np.nan
            dataframe.loc[(year), 'File_Path'] = np.nan
            culled = culled + [year]
    print(f"{culled} have been culled, since these are partial scans ")
    return dataframe


def calculate_growth(dataframe, msoa_name):
    l = len(years)
    time = list(range(0, l))
    x = np.array(time)
    y = dataframe.Volume.to_numpy()
    # mask out NaN
    mask = ~np.isnan(x) & ~np.isnan(y)
    A = np.vstack([x, np.ones(len(x))]).T
    # linearly generated sequence
    m, c = np.linalg.lstsq(A[mask], y[mask], rcond=None)[0]

    plt.plot(x, y, 'o', label='Original data', markersize=10)
    _ = plt.plot(x, m * x + c, 'r', label='Fitted line')
    _ = plt.legend()
    print(f'yearly growth is , {m:.0f} m^3, original volume is {c:.0f} m^3')
    growth = m / c * 100
    print(f'volumes grow by {growth:.2f}% every year')
    plt.show()
    plt.savefig(f"{msoa_name}/{msoa_name}_scatter_plot.png")
    return growth


def crop_raster(raster, shape_in, year):
    raster_out_path = f"/Users/mykolamurashko/Documents/DISSERTATION/Longitudonal study/visualise_lidar/Temp/temp_raster_{year}.tif"
    with fiona.open(shape_in, "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]
    with rasterio.open(raster) as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, nodata=0, crop=True)
        out_meta = src.meta
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    with rasterio.open(raster_out_path, "w", **out_meta) as dest:
        dest.write(out_image)
    return raster_out_path


def show_2D(path, year, msoa_name, growth):
    destination = f'{msoa_name}/{file_type}_{msoa_name}_{year}.png'
    src = rasterio.open(path)
    array = src.read(1)
    fig = pyplot.figure(figsize=(6, 4))
    ax = pyplot.axes(xticks=[], yticks=[])
    ax.imshow(array, cmap='binary', vmin=0, vmax=50)
    ax.set_title((str(year)), fontsize=5, fontweight='bold')
    pyplot.figtext(0.5, 0.075, f"development growth rate in {msoa_name} is {growth:.2f}% a year", ha="center",
                   fontsize=5)
    pyplot.savefig(destination, dpi=500, cmap='binary', vmin=0, vmax=50)
    return destination


def delete_temp_contents():
    import os, shutil
    folder = '/Users/mykolamurashko/Documents/DISSERTATION/Longitudonal study/visualise_lidar/Temp'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def make_gif(filenames, msoa_name):
    images = []
    output = f'{msoa_name}/{file_type}_{msoa_name}.gif'
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(output, images, duration=0.5)
    return output


def create_new_folder(name):
    directory = str("/Users/mykolamurashko/Documents/DISSERTATION/Longitudonal study/visualise_lidar") + str(
        f"/{name}")
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)
    return directory


# call the main() function.
if __name__ == '__main__':
    main()
