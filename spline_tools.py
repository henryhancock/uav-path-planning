import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splev, splprep
import numpy.linalg
from dubins_path import dubins_path, sample_dubins_path

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

    left = np.column_stack((x + offset * nx, y + offset * ny))
    right = np.column_stack((x - offset * nx, y - offset * ny))

    l_spline, r_spline = fit_spline(left), fit_spline(right)
    l_r_splines = (l_spline,r_spline, left, right)

    return l_r_splines

def join_paths(left, right, tck_l, tck_r, r_min):
    """ connect two splines given a minimum turn radius
    args:
    left : positional data for left offset
    right: position data for right offset
    R_min : minimum turn radius
    """
    n = 100
    end_l, end_r = left[-1], right[-1]

    v_tangent_l = np.array(left[-1] - left[-2])
    v_tangent_r = np.array(right[-1] - right[-2])

    theta_l = np.arctan2(v_tangent_l[1], v_tangent_l[0])
    theta_r = np.arctan2(v_tangent_r[1], v_tangent_r[0]) + np.pi

    p1 = (end_l[0],end_l[1],theta_l)
    p2 = (end_r[0],end_r[1],theta_r)



    points, info = sample_dubins_path(p1, p2, r_min, step=0.5)

    full_path = np.concatenate([left, points[1:-1, :2], right[::-1]], axis=0)

    full_path_spline = fit_spline(full_path)

    return (full_path, full_path_spline, points)

    