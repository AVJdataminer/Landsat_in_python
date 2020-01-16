#Bring in the raw .tar file and unpack them.
import os
import tarfile

#Create output folder
newFolder = "LandsatData2018"
os.makedirs(newFolder)

#Extract files
os.chdir(os.path.join(et.io.HOME, 'documents/'))
tar = tarfile.open("Landsat_data/LC081920352018031001T1-SC20190601181703.tar.gz", "r:gz")
tar.extractall(newFolder)
tar.close()

###Now do the stacking and manipulation#####
import os
import numpy as np
# File manipulation
from glob import glob

import matplotlib.pyplot as plt
import matplotlib as mpl

import rasterio as rio
import geopandas as gpd
import earthpy as et
import earthpy.spatial as es
import earthpy.plot    as ep
# if you get a library_spatial index error, run this in the consol:
#   brew install spatialindex

#retry imports


#et.data.get_data('cold-springs-fire')
#Make your base directory
os.chdir(os.path.join(et.io.HOME, 'Documents/Landsat_data/')) 
#/Users/scotthillard/Documents/Landsat_data/LandsatData2018
#set parameters  for display#############
mpl.rcParams['figure.figsize'] = (10, 10)
mpl.rcParams['axes.titlesize'] = 20
###make a list of landsat files
#glob("LC080340322016072301T1-SC20180214145802/crop/*") #grabs all the files
all_landsat_post_bands=glob("LandsatData2019/*band*.tif") #grab only 'band' files
all_landsat_post_bands

#oragnize the data and view the data#
all_landsat_post_bands.sort()
all_landsat_post_bands


#View a raster object in Python------------------------------------#
with rio.open(all_landsat_post_bands[3]) as src:
    landsat_band4 = src.read()

ep.plot_bands(landsat_band4[0],
              title="Landsat_2019_Time1",
              cmap="Greys_r")

#-Create a stack object in python---------------------------------#
#landsat band stack-----------------------------------------------#

landsat_Time2_path = "/Users/scotthillard/Documents/Landsat_data/outputs/landsat_time2_2019.tif"
es.stack(all_landsat_post_bands,landsat_Time2_path, nodata=None)

#open the new raster stack
with rio.open(landsat_Time2_path) as src:
    landsat_Time2_path = src.read()

#rename bands
band_titles = ["Band 1", "Blue", "Green", "Red", "NIR",
               "Band 6", "Band7"]

#plot them all together
ep.plot_bands(landsat_Time2_path,
              title=band_titles,
              cmap="Greys_r")

#plot a composite RGB image###
ep.plot_rgb(landsat_Time2_path,
            rgb=[3, 2, 1],
            title="RGB Composite Image time2")

#plot it again, this time stretch it so that it looks better-stretch 1
ep.plot_rgb(landsat_Time2_path,
            rgb=[3, 2, 1],
            title="Landsat RGB Image time 1",
            stretch=True,
            str_clip=1)


# Adjust the amount of linear stretch to futher brighten the image-stretch 2
ep.plot_rgb(landsat_Time2_path,
            rgb=[3, 2, 1],
            title="Landsat RGB Image\n Linear Stretch Applied",
            stretch=True,
            str_clip=3)

# Here is a CIR image
ep.plot_rgb(landsat_Time2_path, rgb=[4, 3, 2],
            title="CIR Landsat Image Pre-Coldsprings Fire",
            figsize=(10, 10))

#Plot a histogram of the bands
ep.hist(landsat_Time2_path, title= band_titles)

##Now that you have a sweet sweet stack, get the NDVI and the burn ratio

#NDVI =(NIR/red)/(nir+red)-this worked
T2_ndvi = (landsat_Time2_path[4] - landsat_Time2_path[3]) / (landsat_Time2_path[4] + landsat_Time2_path[3])

fig, ax = plt.subplots(figsize=(12,6))
ndvi = ax.imshow(T2_ndvi, cmap='PiYG',
                vmin=-1, vmax=1)
fig.colorbar(ndvi, fraction=.05)
ax.set(title="Landsat Derived NDVI time 2")
ax.set_axis_off()
plt.show()

#Normalized burn index NBR=(NIR-SWIR)/(NIR+SWIR)-remember to that everything index to 0,
#so 5 is 4 and do on 3 is 4, you get the idea
naip_nbr = (landsat_Time2_path[4] - landsat_Time2_path[6]) / (landsat_Time2_path[4] + landsat_Time2_path[6])

fig, ax = plt.subplots(figsize=(12,6))
nbr = ax.imshow(naip_nbr, cmap='PiYG',
                vmin=-1, vmax=1)
fig.colorbar(nbr, fraction=.05)
ax.set(title="Landat Derived Nbr time 1")
ax.set_axis_off()
plt.show()

#export as a .tif-------------------------------------------------------------------------#
landsat_nbr_path = "/Users/scotthillard/Documents/Landsat_data/outputs/LS_2019/nbr_time2.tif"
landsat_ndvi_path = "/Users/scotthillard/Documents/Landsat_data/outputs/LS_2019/ndvi_time2.tif"
type(naip_nbr), naip_nbr.dtype

#in order to view it, you need to be able to export it as a .tif, get the meta data of another source

with rio.open("/Users/scotthillard/Documents/Landsat_data/outputs/landsat_time2_2019.tif") as src:
    naip_data_ras = src.read()
    naip_meta = src.profile
       
naip_meta
# change the count or number of bands from 4 to 1
naip_meta['count'] = 1
# change the data type to float rather than integer
naip_meta['dtype'] = "float64"
#write the raster object
with rio.open(landsat_nbr_path, 'w', **naip_meta) as dst:
    dst.write(naip_nbr, 1)

with rio.open(landsat_ndvi_path, 'w', **naip_meta) as dst:
    dst.write(T2_ndvi, 1)
######---------------------CLassification---------------------------------------------------###
#unsuprevised classification#####-kmeans
    
from spectral import *
import spectral.io.envi as envi
import pandas as pd
from sklearn import cluster
import gdal
#you already have the other packages loaded

dataset = gdal.Open("/Users/scotthillard/Desktop/earth_analytics/coldspringsfire/outputs/nbr.tif")
band = dataset.GetRasterBand(1)
img = dataset.ReadAsArray()
X = img.reshape((-1, 1))
k_means = cluster.KMeans(n_clusters=8)
k_means.fit(X)
X_cluster = k_means.labels_
X_cluster = X_cluster.reshape(img.shape)
plt.figure(figsize=(5,5))
plt.imshow(X_cluster, cmap="hsv")
plt.show()

##Write it to a raster object##
with rio.open(landsat_nbr_path, 'w', **naip_meta) as dst:
    dst.write(X_cluster, 1)






