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


et.data.get_data('cold-springs-fire')
#Make your base directory
os.chdir(os.path.join(et.io.HOME, 'desktop/earth_analytics/coldspringsfire/landsat_collect')) 
#set parameters  for display#############
mpl.rcParams['figure.figsize'] = (10, 10)
mpl.rcParams['axes.titlesize'] = 20
###make a list of landsat files
glob("LC080340322016072301T1-SC20180214145802/crop/*") #grabs all the files
all_landsat_post_bands=glob("LC080340322016072301T1-SC20180214145802/crop/*band*.tif") #grab only 'band' files
all_landsat_post_bands

#oragnize the data and view the data#
all_landsat_post_bands.sort()
all_landsat_post_bands


#View a raster object in Python------------------------------------#
with rio.open(all_landsat_post_bands[3]) as src:
    landsat_band4 = src.read()

ep.plot_bands(landsat_band4[0],
              title="Landsat Cropped Band 4\nColdsprings Fire Scar",
              cmap="Greys_r")

#-Create a stack object in python---------------------------------#
#landsat band stack-----------------------------------------------#

landsat_post_fire_path = "/Users/scotthillard/Desktop/earth_analytics/coldspringsfire/outputs/landsat_post_fire.tif"
es.stack(all_landsat_post_bands,landsat_post_fire_path, nodata=None)

#open the new raster stack
with rio.open(landsat_post_fire_path) as src:
    landsat_post_fire = src.read()

#rename bands
band_titles = ["Band 1", "Blue", "Green", "Red", "NIR",
               "Band 6", "Band7"]

#plot them all together
ep.plot_bands(landsat_post_fire,
              title=band_titles,
              cmap="Greys_r")

#plot a composite RGB image###
ep.plot_rgb(landsat_post_fire,
            rgb=[3, 2, 1],
            title="RGB Composite Image\n Post Fire Landsat Data")

#plot it again, this time stretch it so that it looks better-stretch 1
ep.plot_rgb(landsat_post_fire,
            rgb=[3, 2, 1],
            title="Landsat RGB Image\n Linear Stretch Applied",
            stretch=True,
            str_clip=1)


# Adjust the amount of linear stretch to futher brighten the image-stretch 2
ep.plot_rgb(landsat_post_fire,
            rgb=[3, 2, 1],
            title="Landsat RGB Image\n Linear Stretch Applied",
            stretch=True,
            str_clip=3)

# Here is a CIR image
ep.plot_rgb(landsat_post_fire, rgb=[4, 3, 2],
            title="CIR Landsat Image Pre-Coldsprings Fire",
            figsize=(10, 10))
CIR_Landsat=
#Plot a histogram of the bands
ep.hist(landsat_post_fire, title= band_titles)

##Now that you have a sweet sweet stack, get the NDVI and the burn ratio

#NDVI =(NIR/red)/(nir+red)-this worked
naip_ndvi = (landsat_post_fire[4] - landsat_post_fire[3]) / (landsat_post_fire[4] + landsat_post_fire[3])

fig, ax = plt.subplots(figsize=(12,6))
ndvi = ax.imshow(naip_ndvi, cmap='PiYG',
                vmin=-1, vmax=1)
fig.colorbar(ndvi, fraction=.05)
ax.set(title="Landsat Derived NDVI\n 19 September 2015 - Cold Springs Fire, Colorado")
ax.set_axis_off()
plt.show()

#Normalized burn index NBR=(NIR-SWIR)/(NIR+SWIR)-remember to that everything index to 0,
#so 5 is 4 and do on 3 is 4, you get the idea
naip_nbr = (landsat_post_fire[4] - landsat_post_fire[6]) / (landsat_post_fire[4] + landsat_post_fire[6])

fig, ax = plt.subplots(figsize=(12,6))
nbr = ax.imshow(naip_nbr, cmap='PiYG',
                vmin=-1, vmax=1)
fig.colorbar(nbr, fraction=.05)
ax.set(title="Landat Derived Nbr\n 19 September 2015 - Cold Springs Fire, Colorado")
ax.set_axis_off()
plt.show()

#export as a .tif-------------------------------------------------------------------------#
landsat_nbr_path = "/Users/scotthillard/Desktop/earth_analytics/coldspringsfire/outputs/nbr.tif"
type(naip_nbr), naip_nbr.dtype

#in order to view it, you need to be able to export it as a .tif, get the meta data of another source

with rio.open("/Users/scotthillard/Desktop/earth_analytics/coldspringsfire/outputs/landsat_post_fire.tif") as src:
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

######---------------------CLassification---------------------------------------------------###

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






