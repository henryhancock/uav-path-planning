import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import unary_union

def load_river_polygon(path, crs=26916):
    gdf = gpd.read_file(path).to_crs(crs)
    merged = unary_union(gdf.geometry)
    if merged.geom_type == "MultiPolygon":
        merged = max(merged.geoms, key=lambda g: g.area)
    return Polygon(merged.exterior)