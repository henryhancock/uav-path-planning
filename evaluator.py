import numpy as np
from scipy.interpolate import splev
from shapely.geometry import LineString
from skimage.morphology import medial_axis

from find_longest_path import find_longest_skeleton_path
from preprocessor import load_river_polygon
from rasterize import poly_to_raster
from spline_tools import fit_spline, join_paths, offset_spline


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
    coverage = path.buffer(swath/2)

    covered_area_polygon = river_poly.intersection(coverage)

    total_river_area = river_poly.area
    percent_river_covered = 100 * covered_area_polygon.area / river_poly.area

    print(f"path length {path.length:,.0f} m, covers {percent_river_covered:.1f}% of river corridor ({total_river_area:,.0f} sq m)")
    return percent_river_covered, covered_area_polygon, path.length


def extract_centerline(river_polygon, pixel_size, pad):
    """Rasterizes the river polygon and extracts its medial-axis centerline.
    args:
    river_polygon : shapely Polygon of the river corridor
    pixel_size : raster pixel size in meters
    pad : raster padding in pixels

    return: (longest centerline path, width at every point along the centerline)
    """
    rasterized_river, _transform = poly_to_raster(river_polygon, pixel_size, pad)

    skeleton_line, distance_map = medial_axis(rasterized_river, return_distance=True)
    width_along_centerline = distance_map * skeleton_line * pixel_size

    long_skel, _skel_len = find_longest_skeleton_path(skeleton_line, True)

    return long_skel, width_along_centerline


def centerline_to_flight_path(long_skel, river_polygon, pixel_size, pad, r_min, n_samples):
    """Fits a spline to the centerline, offsets it into left/right passes joined
    by a Dubins turn, and maps the result back into the river polygon's CRS.
    args:
    long_skel : longest path along the skeleton, in raster row/col coordinates
    river_polygon : shapely Polygon of the river corridor, used to place the raster origin
    pixel_size : raster pixel size in meters
    pad : raster padding in pixels
    r_min : minimum turn radius of the aircraft
    n_samples : number of points to sample along the joined flight path

    return: flight path as an (N, 2) array of x, y coordinates
    """
    tck, _u = fit_spline(long_skel, 10000)

    l_spline, r_spline, left, right = offset_spline(tck, 30, 4000)
    _full_path, full_path_spline, _dubins_points = join_paths(left, right, l_spline[0], r_spline[0], r_min)

    s = np.linspace(0, 1, n_samples)
    r, c = splev(s, full_path_spline[0])

    minx, miny, maxx, maxy = river_polygon.bounds
    x = minx - pad * pixel_size + c * pixel_size
    y = maxy + pad * pixel_size - r * pixel_size
    return np.column_stack([x, y])


def test_river(river_data=None, river_polygon=None, pixel_size=1, pad=10, swath=120, offset=40, r_min=40, n_samples=2000):
    """Runs the full pipeline: raster -> skeleton -> spline -> evaluate.
    args:
    river_data : path to a GeoJSON file (used only if river_polygon is not given)
    river_polygon : an already-built shapely Polygon (e.g. from sin_river), skips geotester
    """
    if river_polygon is None:
        river_polygon = load_river_polygon(river_data)

    long_skel, width_along_centerline = extract_centerline(river_polygon, pixel_size, pad)

    widths, needs_multiple_passes = evaluate_width(width_along_centerline, long_skel, swath)

    flight_path = centerline_to_flight_path(long_skel, river_polygon, pixel_size, pad, r_min, n_samples)

    pct, covered, path_length = evaluate_path(flight_path, river_polygon, swath)

    return {
        "coverage_pct": pct,
        "path_length_m": path_length,
        "widths": widths,
        "frac_needing_multipass": float(needs_multiple_passes.mean()),
        "river_polygon": river_polygon,
        "flight_path": flight_path,
    }