import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splev, splprep
import numpy.linalg

# river x vals are not strictly increasing, using parametric spline fit
def fit_spline(river_points, smoothing=0, degree=3):
    """fits a spline among a series of points
    args:
    river_points: ordered row,col points the spline is fit along
    smoothing: degree to which spline is forced. 0 = line goes through every point
    degree: degree of 3 ensures a continuous curve
    """
    x, y = zip(*river_points)
    tck, u = splprep([x, y], s=smoothing, k=degree)
    #tck defines spline rule input -> output
    return tck, u

def find_curvature(tck, n=2000):
    """finds curvature along spline with given sampling rate
    args:
    tck: spline 'rule'
    n(int): number of samples taken along the line
    """
    u = np.linspace(0, 1, n)
    dx, dy = splev(u, tck, der=1)
    ddx, ddy = splev(u, tck, der=2)

    num = np.abs(dx * ddy - dy * ddx)
    den = (dx**2 + dy**2)**1.5
    kappa = num / np.maximum(den, 1e-12) #curvature of parametric curve

    x, y = splev(u, tck)
    return u, np.array(x), np.array(y), kappa

def offset_spline(tck, offset, n = 4000):
    """ Generates offset splines
    args:
    tck: spline rule
    offset: distance to offset the path
    n: sampling rate

    return:
    l_r_splines : tuples with the tck for the offset splines as well as xy data
    """
    u = np.linspace(0, 1, n)
    x, y = splev(u, tck)
    dx, dy = splev(u, tck, der=1)

    mag = np.sqrt(dx**2 + dy**2)
    mag = np.maximum(mag, 1e-12)

    ux, uy = dx / mag, dy / mag
    nx, ny = -uy, ux

    # np arrays
    left = np.column_stack((x + offset * nx, y + offset * ny))
    right = np.column_stack((x - offset * nx, y - offset * ny))

    l_spline, r_spline = fit_spline(left), fit_spline(right)
    l_r_splines = (l_spline,r_spline, left, right)

    return l_r_splines

def join_paths(left, right, tck_l, tck_r, R_min):
    """ connect two splines given a minimum turn radius
    args:
    left : positional data for left offset
    right: position data for right offset
    R_min : minimum turn radius
    """
    n = 100
    end_l, end_r = left[-1], right[-1]
    P = (end_l + end_r) / 2
    R = np.linalg.norm(end_l - P)

    start_angle = np.arctan2(end_l[1] - P[1], end_l[0] - P[0])
    
    # Track direction vector to ensure cap loops forward
    v_tangent = np.array(left[-1] - left[-2])
    
    # Determine correct sweep direction (+pi or -pi)
    mid_angle = start_angle + np.pi / 2
    v_mid = np.array([np.cos(mid_angle), np.sin(mid_angle)])
    
    if np.dot(v_mid, v_tangent) < 0:
        end_angle = start_angle - np.pi
    else:
        end_angle = start_angle + np.pi
        
    # Generate semicircular coordinates
    angles = np.linspace(start_angle, end_angle, n)
    x = P[0] + R * np.cos(angles)
    y = P[1] + R * np.sin(angles)
    
    connector = np.column_stack((x, y))
    full_path = np.concatenate([left, connector[1:-1], right[::-1]], axis=0)

    full_path_spline = fit_spline(full_path)

    return (full_path, full_path_spline, connector)

    