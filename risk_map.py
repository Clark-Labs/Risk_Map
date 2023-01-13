import os
import numpy as np
from osgeo import gdal

### USER INPUT###
# #Input NRT number from user as float32, [2460]
# NRT = np.float32(input("Please Enter NRT (Negligible Risk Threshold) Distance: "))
#
# #Input numbers of non-zero classes from user as int, [30]
# n_classes = int(input("Please Enter Number of non-zero classes: "))
#
# #Input filename of the output image from user as string, [risk30.rst]
# out_fn = input("Filename for the output image: ")


### SET UP CURRENT WORKING DIRECTORY###
os.chdir(r'C:\Document\ClarkLab\automation team\TerraCarbon')


### INPUT "MAP OF DISTANCE FROM THE FOREST EDGE" FILE###
in_fn = 'dist_nf14_mask_acre.rst'


### CONVERT RASTER TO NumPy ARRAY###
# Set up a GDAL dataset
in_ds = gdal.Open(in_fn)

# Set up a GDAL band
in_band = in_ds.GetRasterBand(1)

# Create Numpy Array
arr = in_band.ReadAsArray()


###CREATE A GEOMETRIC SERIES CLASSIFICATION###
"""
LL: the lower limit of the highest risk class = spatial resolution (the minimum distance possible without being in non-forest)
UL: the upper limit of the lowest risk class = the Negligible Risk Threshold
LLc: lower limit of the class
n_classes: number of classes
"""
LL = xres= in_ds.GetGeoTransform()[1]
UL = NRT = 2460
n_classes = 30
# Calculate common ratio(r)
r = np.power(LL / UL, 1/n_classes)
# print("Common ratio : ",r)

# Create an empty class array to generate a list of LLc value
class_array = []
for c in range(n_classes):
    LLc = UL * r**c
    class_array.append(LLc)
class_array.append(xres)
#print(class_array)

# Create a new class array include ULc and LLc in each class
class_array_n = []
i=0
for i in range(n_classes):
    a = class_array[i:i+2]
    i+=1
    class_array_n.append(a)
#print(class_array_n)


###RECLASSIFY DISTANCE MAP###
# Create NRT Mask array
mask_arr = np.ma.masked_where(arr >= NRT , arr)
mask_arr = mask_arr.filled(0)

# Reclassification
index=0
for UL, LL in class_array_n:
    mask_arr[np.where((UL > mask_arr) & (mask_arr >= LL))] = index+1
    index+=1
#print(mask_arr)


###EXPORT MAP OF RISK###
# Define a function to convert array to raster file
def array2raster(in_ds, out_fn, data, data_type, nodata=None):
    """Create a one-band GeoTIFF.
    in_ds - datasource to copy projection and geotransform from
    out_fn - path to the file to create
    data - NumPy array containing data to write
    data_type - output data type
    nodata - optional NoData value
    """
    driver =  in_ds.GetDriver()
    out_ds = driver.Create(
        out_fn, in_ds.RasterXSize, in_ds.RasterYSize, 1, data_type)
    out_ds.SetProjection(in_ds.GetProjection())
    out_ds.SetGeoTransform(in_ds.GetGeoTransform())
    out_band = out_ds.GetRasterBand(1)
    out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])
    if nodata is not None:
        out_band.SetNoDataValue(nodata)
        out_band.WriteArray(data)
        out_band.FlushCache()
        out_band.ComputeStatistics(False)
        return out_ds
    del in_ds, out_ds

# Run export task
out_fn = 'risk30.rst'
out_ds = array2raster(
in_ds, out_fn, mask_arr, gdal.GDT_Float32, -99)