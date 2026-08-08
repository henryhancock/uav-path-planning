import numpy as np
from shapely.geometry import Polygon
from skimage.morphology import skeletonize
from skimage import data
import matplotlib.pyplot as plt
from skimage.morphology import medial_axis
from skimage.util import invert
import rasterio.features
from sine_river import sin_river


# --- geometry ---
center, boundary = sin_river()
sin_poly = Polygon(boundary)

minx, miny, maxx, maxy = sin_poly.bounds
width_meters = maxx - minx
height_meters = maxy - miny

pixel_size = 1.0 # meters
pad = 10 #pixels

grid_width = int(np.ceil(width_meters /  pixel_size))
grid_height = int(np.ceil(height_meters /  pixel_size))

#maps x,y to pixels
transform = rasterio.transform.from_bounds(
    minx, miny, maxx, maxy, grid_width, grid_height
)

#reads map and plots
raster_mask = rasterio.features.rasterize(
    [sin_poly],
    out_shape=(grid_height, grid_width),
    transform=transform,
    fill=0,
    default_value=1,
    dtype=np.uint8
)

#medial axis returns binary skeleton + distance heat map
skel_line, distance_map = medial_axis(raster_mask, return_distance=True)


width_along_centerline = distance_map * skel_line

fig, axes = plt.subplots(1, 3, figsize=(12, 4))

axes[0].imshow(raster_mask, cmap='gray')
axes[0].set_title("1. Original Raster Mask")

axes[1].imshow(distance_map, cmap='viridis')
axes[1].set_title("2. Full Distance Map")

axes[2].imshow(width_along_centerline, cmap='magma')
axes[2].set_title("3. Medial Axis Centerline")

plt.tight_layout()
plt.show()
