from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from skimage.morphology import medial_axis
from sine_river import sin_river
from rasterize import poly_to_raster
from geotester import load_river_polygon

#globals, pixel size = resolution, pad = border thickness
pixel_size = 1.0 # meters
pad = 10 #pixels


center, boundary = sin_river()
sin_poly = Polygon(boundary)
riv_poly = load_river_polygon("fox_snippet.geojson")

raster_mask,transform = poly_to_raster(riv_poly,pixel_size,pad)

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
