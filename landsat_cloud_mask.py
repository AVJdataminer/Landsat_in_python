from glob import glob
import os

import numpy.ma as ma
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches as mpatches, colors
from matplotlib.colors import ListedColormap
import matplotlib as mpl
import seaborn as sns

import rasterio as rio
from rasterio.plot import plotting_extent
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping

import earthpy as et
import earthpy.spatial as es

plt.ion()
sns.set_style('white')
sns.set(font_scale=1.5)

os.chdir(os.path.join(et.io.HOME, 'earth-analytics'))


# Stack the landsat pre fire data
landsat_paths_pre = glob(
    "data/cold-springs-fire/landsat_collect/LC080340322016070701T1-SC20180214145604/crop/*band*.tif")
path_landsat_pre_st = 'data/cold-springs-fire/outputs/landsat_pre_st.tif'
es.stack_raster_tifs(landsat_paths_pre, path_landsat_pre_st, arr_out=False)

# Read landsat pre fire data
with rio.open(path_landsat_pre_st) as landsat_pre_src:
    landsat_pre = landsat_pre_src.read(masked=True)
    landsat_extent = plotting_extent(landsat_pre_src)

 Define Landast bands for plotting homework plot 1
landsat_rgb = [3, 2, 1]

fig, ax = plt.subplots(1, 1, figsize=(10, 6))

es.plot_rgb(landsat_pre,
            rgb=landsat_rgb,
            ax=ax,
            extent=landsat_extent)

ax.set(title="Landsat CIR Composite Image | 30 meters \n Post Cold Springs Fire \n July 8, 2016")
ax.set_axis_off()
plt.show()

# Open the pixel_qa layer for your landsat scene
with rio.open(
    "data/cold-springs-fire/landsat_collect/LC080340322016070701T1-SC20180214145604/crop/LC08_L1TP_034032_20160707_20170221_01_T1_pixel_qa_crop.tif") as landsat_pre_cl:
    landsat_qa = landsat_pre_cl.read(1)
    landsat_ext = plotting_extent(landsat_pre_cl)

cmap = plt.cm.get_cmap('tab20b', 11)
vals = np.unique(landsat_qa).tolist()
bins = [0] + vals
bounds = [((a + b) / 2) for a, b in zip(bins[:-1], bins[1::1])] + [(bins[-1] - bins[-2]) + bins[-1]]
norm = colors.BoundaryNorm(bounds, cmap.N)

fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(landsat_qa,
               cmap=cmap,
              norm=norm)

ax.set_title("Landsat Collections Pixel_QA Layer \n The colorbar is currently a bit off but will be fixed")
ax.set_axis_off()
plt.show()

# pre-allocate an array of all zeros representing the same sized array as the landsat scene and cloud mask
cl_mask = np.zeros(landsat_qa.shape)


# pre-allocate an array of all zeros representing the same sized array as the landsat scene and cloud mask
cl_mask = np.zeros(landsat_qa.shape)

# Generate array of all possible cloud / shadow values
water = [324, 388, 836, 900, 1348]
cloud_shadow = [328, 392, 840, 904, 1350]
cloud = [352, 368, 416, 432, 480, 864, 880, 928, 944, 992]
high_confidence_cloud = [480, 992]

all_masked_values = cloud_shadow + cloud + high_confidence_cloud
all_masked_values


##Plot the cloud mask
fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(cl_mask,
               cmap=plt.cm.get_cmap('tab20b', 2))
cbar = fig.colorbar(im)
cbar.set_ticks((0.25, .75))
cbar.ax.set_yticklabels(["Clear Pixels", "Cloud / Shadow Pixels"])
ax.set_title("Landsat Cloud Mask | Light Purple Pixels will be Masked")
ax.set_axis_off()

plt.show()


# Create a mask for all bands in the landsat scene
landsat_pre_mask = np.broadcast_to(cl_mask == 1, landsat_pre.shape)
landsat_pre_cl_free = ma.masked_array(landsat_pre,
                                      mask=landsat_pre_mask)
type(landsat_pre_cl_free)
##numpy.ma.core.MaskedArray

# Plot the data
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

ax.imshow(landsat_pre_cl_free[6],
          extent=landsat_extent,
          cmap="Greys")
ax.set(title="Landsat CIR Composite Image | 30 meters \n Post Cold Springs Fire \n July 8, 2016")
ax.set_axis_off()

# Plot
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

es.plot_rgb(landsat_pre_cl_free,
            rgb=[5, 4, 3],
            extent=landsat_ext,
            ax=ax)
ax.set(title="Landsat CIR Composite Image | 30 meters \n Post Cold Springs Fire \n July 8, 2016")
ax.set_axis_off()




