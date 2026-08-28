from shapely.geometry import Polygon
import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import medial_axis
from sine_river import sin_river
from rasterize import poly_to_raster
from preprocessor import load_river_polygon
from SplineTools import fit_spline, find_curvature, offset_spline, join_paths
from find_longest import find_longest_skeleton_path
from scipy.interpolate import splev, splprep

from shapely.geometry import LineString

def evaluate_width(width_along_centerline,long_skel, swath=127.6):
    """Determines whether the width along the centerline exceeds the sensor swath at any points
    args:
    width_along_centerline : width of the river at every point in the centerline
    long_skel : longest path along centerline
    swath(float) : sensor swath of given vehicle
    """

    skel = np.asarray(long_skel)
    widths = 2 * width_along_centerline[skel[:, 0], skel[:, 1]]

    needs_multiple_passes = widths > swath
    print(f"swath {swath:.1f} m, river width {widths.min():.0f}-{widths.max():.0f} m")
    print(f"{100*needs_multiple_passes.mean():.1f}% of centerline wider than one swath")
    
    return widths, needs_multiple_passes

def evaluate_path(flight_path, river_poly, swath):

    path = LineString(flight_path)
    print("simulating flight...")
    coverage = path.buffer(swath/2)

    covered_area_polygon = river_poly.intersection(coverage)

    total_river_area = river_poly.area
    percent_river_covered = 100 * covered_area_polygon.area / river_poly.area

    print(f"the total river area is {total_river_area:,.0f} square meters")
    print(f"path length {path.length:,.0f} m")
    print(f"this path covers {percent_river_covered:.1f}% of the river corridor")
    return percent_river_covered, covered_area_polygon

def test_river(river_data=None, river_polygon=None, pixel_size=1, pad=10, swath=120, offset=40, r_min = 40, n_samples=2000):
    """Runs the full pipeline: raster -> skeleton -> spline -> evaluate.
    args:
    river_data : path to a GeoJSON file (used only if river_polygon is not given)
    river_polygon : an already-built shapely Polygon (e.g. from sin_river), skips geotester
    """
    if river_polygon is None:
        print("Loading river data...")
        river_polygon = load_river_polygon(river_data)

    print("Rasterizing river polygon...")
    rasterized_river, origin = poly_to_raster(river_polygon, pixel_size, pad)

    print("Running medial axis transform...")
    skeleton_line, distance_map = medial_axis(rasterized_river, return_distance=True)
    width_along_centerline = distance_map * skeleton_line * pixel_size

    print("Finding longest path...")
    long_skel, skel_len = find_longest_skeleton_path(skeleton_line, True)

    print("Evaluating width...")
    widths, needs_multiple_passes = evaluate_width(width_along_centerline,
                                                   long_skel, swath)

    print("Fitting spline...")
    tck, u = fit_spline(long_skel,10000)


    l_spline,r_spline, left, right = offset_spline(tck, 30, 4000)
    fp,fps,p = join_paths(left, right, l_spline[0], r_spline[0],r_min)

    s = np.linspace(0, 1, n_samples)
    r, c = splev(s, fps[0])

    minx, miny, maxx, maxy = river_polygon.bounds
    x = minx - pad * pixel_size + c * pixel_size
    y = maxy + pad * pixel_size - r * pixel_size
    flight_path = np.column_stack([x, y])

    print("Evaluating the flight path...")
    pct, covered = evaluate_path(flight_path, river_polygon, swath)

    print("path  ", LineString(flight_path).bounds)
    print("river ", river_polygon.bounds)
    return {
        "coverage_pct": pct,
        "path_length_m": skel_len * pixel_size,
        "widths": widths,
        "frac_needing_multipass": float(needs_multiple_passes.mean()),
        "river_polygon": river_polygon,
        "flight_path": flight_path,
    }