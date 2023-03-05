import os
import numpy as np
from osgeo import gdal

### USER INPUT###
#Input NRT number from user as float32, e.g., 2460.
NRT = np.float32(input("Please Enter NRT (Negligible Risk Threshold) Distance: "))

#Input numbers of non-zero classes from user as int, e.g., 30.
n_classes = int(input("Please Enter Number of non-zero classes: "))

#Input filename of the output image from user as string, e.g., risk30.
out_fn = input("Filename for the output image: ")

#Input current working directory
path = input("Current working directory: ")


### SET UP CURRENT WORKING DIRECTORY###
os.chdir(path)


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
UL = NRT 

# Calculate common ratio(r)
r = np.power(LL / UL, 1/n_classes)
# print("Common ratio : ",r)

#Create 2D 30 class_array and sort from class 1 to 30
class1=np.arange(1,31).reshape(15, 2)
class2=np.arange(0,30).reshape(15, 2)
class_array=np.concatenate((class1,class2))
class_array=sorted(class_array, key=lambda x: x[1])
# print(class_array)

# Calculate UL and LL value in each class
x= np.power(r, class_array)
risk_class=np.multiply(UL,x)
# print(risk_class)

###RECLASSIFY DISTANCE MAP###
# Create NRT Mask array
mask_arr = np.ma.masked_where(arr >= NRT , arr)
mask_arr = mask_arr.filled(0)

# Reclassification
index=0
for UL, LL in risk_class:
    mask_arr[np.where((UL > mask_arr) & (mask_arr >= LL))] = index+1
    index+=1


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
