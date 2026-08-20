from shapely.geometry import Polygon
import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import medial_axis
from sine_river import sin_river
from rasterize import poly_to_raster
from geotester import load_river_polygon
from SplineTools import fit_spline, find_curvature
from skel_overlay import skel_river_overlay
from find_longest import find_longest_skeleton_path
from evaluator import evaluate_width
from river_plots import plot_all


pixel_size = 1.0 # meters
pad = 10 #pixels


print("loading river data...")
riv_poly = load_river_polygon("fox_snippet.geojson")

print("rasterizing river polygon...")
raster_mask,transform = poly_to_raster(riv_poly,pixel_size,pad)


print("running medial axis transform on river...")
skel_line, distance_map = medial_axis(raster_mask, return_distance=True)
width_along_centerline = distance_map * skel_line


print("finding longest path...")
long_skel, skel_len = find_longest_skeleton_path(skel_line, True)
skel_river_overlay(raster_mask, skel_line,long_skel)

widths = evaluate_width(width_along_centerline, long_skel, 127.6)


tck, u = fit_spline(long_skel,10000)
u, x, y, k = find_curvature(tck)
R = 1 / np.maximum(k, 1e-12)
bad = R < 39.7

plot_all(raster_mask, distance_map, skel_line, long_skel, tck,
         width_along_centerline)