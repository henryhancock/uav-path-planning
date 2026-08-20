import numpy as np
import rasterio.features

def poly_to_raster(poly,pixel_size,pad):
    """Converts river polygon to a raster mask and distance heat map
    args:
    poly: Shapely polygon of river segment
    pixel_size: size of one pixel in meters
    pad: number of pixel along outer edge of image
    
    """
    
    minx, miny, maxx, maxy = poly.bounds
    width_meters = maxx - minx
    height_meters = maxy - miny

    transform = rasterio.transform.from_origin(
    minx - pad * pixel_size,
    maxy + pad * pixel_size,
    pixel_size, pixel_size
)
    grid_width = int(np.ceil(width_meters / pixel_size)) + 2 * pad
    grid_height = int(np.ceil(height_meters / pixel_size)) + 2 * pad
    #reads map and plots
    raster_mask = rasterio.features.rasterize(
        [poly],
        out_shape=(grid_height, grid_width),
        transform=transform,
        fill=0,
        default_value=1,
        dtype=np.uint8,
        all_touched=True
    )
    return raster_mask,transform