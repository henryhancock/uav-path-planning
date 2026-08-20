import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splev, splprep

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
    #at each point add +- offset in perpendicular direction, return 2 sets of tuples
    return 0