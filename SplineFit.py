import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splev, splprep

# river x vals are not strictly increasing, using parametric spline fit

def fit_spline(river_points, smoothing = 0, degree = 3):
    x, y = zip(*river_points)
    num_points = len(river_points)
    tck, _ = splprep([x, y], s=smoothing, k=degree)
    
    u_fine = np.linspace(0, 1, num_points)
    x_smooth, y_smooth = splev(u_fine, tck)
    
    return x_smooth, y_smooth