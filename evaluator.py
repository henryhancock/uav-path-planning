import numpy as np

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
    #sweep the swath over the path and compare against polygon