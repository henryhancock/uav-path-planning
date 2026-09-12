import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import unary_union
from pyproj import Transformer
import numpy as np
from rdp import rdp


def load_river_polygon(path, crs=26916):
    """ Turn GeoJSON data into UTM and remove islands. If multiple chunks exist, the largest is taken
    args: 
    path - path to GeoJSON data
    crs - coordinate reference area

    return: shapely polygon of processed river data
    
    
    
    """
    gdf = gpd.read_file(path).to_crs(crs)
    merged = unary_union(gdf.geometry)
    if merged.geom_type == "MultiPolygon":
        merged = max(merged.geoms, key=lambda g: g.area)
    return Polygon(merged.exterior)