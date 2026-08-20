import numpy as np


def sin_river(amplitude = 100.0, length = 1000.0, wavelength = 500.0,
              half_width = 25, n = 2000):
    """Generates a sinusoidal river for use in testing
    args:
    amplitude(float) : amplitude of waves
    length(float) : length of sinusoidal river in meters
    wavelength(float) : wavelength of sine wave
    half_width(float) : half the distance across width of the river
    n(int) : sampling rate of the sine function
    
    
    """

    # n = # samples along bank

    bottom = []
    center = []
    top = []

    k = (2 * np.pi) / (wavelength)

    for i in range(n):
        x = length * i / (n - 1)
        y = amplitude * np.sin(k*x)
        dydx = amplitude * k * np.cos(k * x)
        theta = np.arctan2(dydx, 1.0)

        nx = -np.sin(theta)
        ny = np.cos(theta)

        center.append((x, y))
        bottom.append((x + half_width * nx, y + half_width * ny))
        top.append((x - half_width * nx, y - half_width * ny))

    boundary = bottom + top[::-1]
    return np.array(center), np.array(boundary)
