import numpy as np
from dubins_path import dubins_path, sample_dubins_path


def generate_lawnmower_points(offset, r_min, river_polygon):
    minx, miny, maxx, maxy = river_polygon.bounds
    width_meters = maxx - minx
    height_meters = maxy - miny

    # assume height > width always

    num_passes = int(np.round(width_meters / offset))
    num_passes = max(num_passes, 2)  # 2 is minimum pass count

    actual_spacing = width_meters / (num_passes - 1)
    print("this requires ", num_passes, "passes at an offset of ", actual_spacing)
    print("distance flown in passes is ", (1/1000)*(num_passes*height_meters), "kilometers")
    passes = []
    for i in range(num_passes):
        x_i = minx + i * actual_spacing

        going_up = (i % 2 == 0)
        if going_up:
            start_pt = (x_i, miny)
            end_pt   = (x_i, maxy)
            heading  = .5*np.pi
        else:
            start_pt = (x_i, maxy)
            end_pt   = (x_i, miny)
            heading  = 1.5*np.pi

        passes.append((start_pt, end_pt, heading))

    return passes

def connect_passes(passes, r_min):
    points = []
    for i in range(len(passes)):
        start_pt1, end_pt1, heading1 = passes[i]
        points.append((start_pt1[0], start_pt1[1], heading1))
        points.append((end_pt1[0], end_pt1[1], heading1))

        if i < len(passes) - 1:
            start_pt2, end_pt2, heading2 = passes[i + 1]
            p1 = (end_pt1[0], end_pt1[1], heading1)
            p2 = (start_pt2[0], start_pt2[1], heading2)
            connector, info = sample_dubins_path(p1, p2, r_min)
            points.extend(connector)

    return points

def generate_lawnmower(offset,r_min,river_polygon):
    passes = generate_lawnmower_points(offset,r_min,river_polygon)
    points = connect_passes(passes,r_min)
    return np.array(points)
