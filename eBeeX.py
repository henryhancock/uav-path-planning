import numpy as np

# stated specs

v_operational = 15 #m/s
h_operational = 120 #m
theta_max = np.radians(30) #radians
g = 9.81 #m/s^2

R_min = (v_operational**2) / (g * np.tan(theta_max)) # 39.7 meters

FOV = np.radians(56) #radians, FOV of camera

w = 2 * h_operational * np.tan(FOV/2) #camera swath, 127 meters

#other parameters
sidelap_value = .25 #25% overlap