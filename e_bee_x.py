import numpy as np

# stated specs

v_operational = 15 #m/s
h_operational = 120 #m
theta_max = np.radians(30) #radians
g = 9.81 #m/s^2


FOV = np.radians(56) #radians, FOV of camera


#other parameters
sidelap_value = .60 #25% overlap


def compute_parameters(airspeed, max_bank, sensor_FOV, AGL, sidelap_pct):
    """ generates relevant flight parameters - minimum turn radius and camera swath
    params:
    airspeed - meters per second, constant cruise speed
    max_bank - maximum bank angle of the aircraft, degrees
    camera_FOV - FOV of attached sensor, degrees
    AGL - above ground level, meters
    sidelap_pct - % of coverage desired to overlap

    returns:
    r_min - minimum turn radius of the aircraft
    swath - sensor swath
    offset - offset required between paths to obtain desired sidelap
    """

    swath = 2 * AGL * np.tan(np.radians(sensor_FOV / 2))
    r_min = (airspeed**2) / (9.81 * np.tan(np.radians(max_bank)))
    offset = (swath / 2) * (1 - sidelap_pct / 100)

    return swath, r_min, offset

