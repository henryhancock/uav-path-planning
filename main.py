from evaluator import test_river
from plot_path import plot_river_path
from eBeeX import compute_parameters

pixel_size = 1.0  # meters
pad = 10  # pixels


swath, r_min, offset = compute_parameters(15, 30, 56,120,60)

result = test_river(river_data="curved_river.geojson", pixel_size=pixel_size, pad=pad, swath=swath,
                     r_min=r_min, offset=offset)

plot_river_path(result["river_polygon"], result["flight_path"])