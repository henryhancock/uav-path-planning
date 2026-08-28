def generate_lawnmower_path(offset, r_min, river_polygon):


    
    minx, miny, maxx, maxy = river_polygon.bounds
    width_meters = maxx - minx
    height_meters = maxy - miny