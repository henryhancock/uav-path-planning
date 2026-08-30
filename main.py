from evaluator import test_river, evaluate_path
from plot_path import plot_river_path
from e_bee_x import compute_parameters
from lawnmower import generate_lawnmower
from preprocessor import load_river_polygon

pixel_size = 1.0  # meters
pad = 10  # pixels


swath, r_min, offset = compute_parameters(15, 30, 56,120,60)
print(offset)
river_polygon = load_river_polygon("fox_snippet.geojson")
# result = test_river(river_data="curved_river.geojson", pixel_size=pixel_size, pad=pad, swath=swath,
#                      r_min=r_min, offset=offset)

lawnmower = generate_lawnmower(offset,r_min,river_polygon)



# plot_river_path(result["river_polygon"], result["flight_path"])
plot_river_path(river_polygon, lawnmower)
