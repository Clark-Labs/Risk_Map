import os
import numpy as np
from osgeo import gdal
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch.optim as optim
import torch.utils.data as data
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from maskedtensor import masked_tensor
# from sklearn import metrics
# from sklearn import decomposition
# from sklearn import manifold
# from tqdm.notebook import trange, tqdm
# import matplotlib.pyplot as plt
# import copy
# import random

start = time.time()

### Create Torch Dataset and Dataloader###
# save_dir = "r'C:\Document\ClarkLab\automation team\TerraCarbon\Risk_Map\data'"
# in_fn = 'dist_nf14_mask_acre.rst'
# image_root= os.path.join(save_dir, in_fn)
#
## Create Torch Dataset
#distance = torchvision.datasets.ImageNet('path/to/image_root/')
#
## Create dataloader
# distance_dataset = datasets.distance(root=save_dir,
#                             train=True,
#                             download=True)

### SET UP CURRENT WORKING DIRECTORY###
os.chdir(r'C:\Document\ClarkLab\automation team\TerraCarbon\Risk_Map\data')

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
#r = torch.pow(LL / UL, 1/n_classes)
# print("Common ratio : ",r)

#Create 2D 30 class_array and sort from class 1 to 30
class1=torch.arange(1,31).reshape(15, 2)
class2=torch.arange(0,30).reshape(15, 2)
class_torch=torch.cat((class1,class2))
class_torch=sorted(class_torch, key=lambda x: x[1])
# print(class_array)

# Calculate UL and LL value in each class
#x= np.power(r, class_array)
x= torch.pow(r, class_torch)
risk_class=torch.matmul(UL,x)
# print(risk_class)

###RECLASSIFY DISTANCE MAP###
# Create NRT Mask array
mask_torch = torch.masked_select(arr >= NRT , arr)
mask_torch = mask_torch.filled(0)
print(mask_torch)

# Reclassification
index=0
for UL, LL in risk_class:
    mask_torch[torch.where((UL > mask_torch) & (mask_torch >= LL))] = index+1
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

end = time.time()
print(end - start)

