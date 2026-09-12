from evaluator import test_river, evaluate_path
from plot_path import plot_river_path
from e_bee_x import compute_parameters
from lawnmower import generate_lawnmower
from preprocessor import load_river_polygon
from rdp import rdp


pixel_size = 1.0  # meters
pad = 10  # pixels

swath, r_min, offset = compute_parameters(15, 30, 56, 120, 60)
print(f"swath={swath:.1f} m, r_min={r_min:.1f} m, offset={offset:.1f} m")

river_polygon = load_river_polygon("fox_snippet.geojson")

# --- lawnmower baseline ---
print("\n--- lawnmower baseline ---")
lawnmower_path = generate_lawnmower(offset, r_min, river_polygon)
lm_pct, lm_covered, lm_length = evaluate_path(lawnmower_path, river_polygon, swath)

# --- spline offset path ---
print("\n--- spline offset path ---")
result = test_river(
    river_polygon=river_polygon,
    pixel_size=pixel_size,
    pad=pad,
    swath=swath,
    offset=offset,
    r_min=r_min,
)
spline_path = result["flight_path"]
print(len(spline_path))
simplified_path = rdp(spline_path, epsilon=1.0) 
print(f"Reduced waypoints from {len(spline_path)} to {len(simplified_path)}")
spline_pct = result["coverage_pct"]
spline_length = result["path_length_m"]

# --- comparison ---
print("\n--- comparison ---")
print(f"lawnmower:      {lm_length/1000:.1f} km, {lm_pct:.1f}% coverage")
print(f"spline offset:  {spline_length/1000:.1f} km, {spline_pct:.1f}% coverage")

reduction_m = lm_length - spline_length
reduction_pct = 100 * reduction_m / lm_length
print(f"reduction: {reduction_m/1000:.1f} km ({reduction_pct:.1f}%)")

plot_river_path(river_polygon, lawnmower_path)
plot_river_path(river_polygon, spline_path)
plot_river_path(river_polygon, simplified_path)
