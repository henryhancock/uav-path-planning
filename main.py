import argparse

from rdp import rdp

from e_bee_x import compute_parameters
from evaluator import evaluate_path, test_river
from lawnmower import generate_lawnmower
from plot_path import plot_river_path
from preprocessor import load_river_polygon


def get_vehicle_parameters(airspeed=15, max_bank=30, fov=56, agl=120, sidelap=60):
    swath, r_min, offset = compute_parameters(airspeed, max_bank, fov, agl, sidelap)
    print(f"swath={swath:.1f} m, r_min={r_min:.1f} m, offset={offset:.1f} m")
    return swath, r_min, offset


def run_lawnmower_baseline(river_polygon, offset, r_min, swath):
    print("\n--- lawnmower baseline ---")
    path = generate_lawnmower(offset, r_min, river_polygon)
    coverage_pct, _covered, path_length_m = evaluate_path(path, river_polygon, swath)
    return {"path": path, "coverage_pct": coverage_pct, "path_length_m": path_length_m}


def run_spline_path(river_polygon, pixel_size, pad, swath, offset, r_min):
    print("\n--- spline offset path ---")
    result = test_river(
        river_polygon=river_polygon,
        pixel_size=pixel_size,
        pad=pad,
        swath=swath,
        offset=offset,
        r_min=r_min,
    )
    flight_path = result["flight_path"]
    simplified_path = rdp(flight_path, epsilon=1.0)
    print(f"Reduced waypoints from {len(flight_path)} to {len(simplified_path)}")
    result["simplified_path"] = simplified_path
    return result


def compare_paths(lawnmower, spline):
    lm_length, lm_pct = lawnmower["path_length_m"], lawnmower["coverage_pct"]
    spline_length, spline_pct = spline["path_length_m"], spline["coverage_pct"]

    reduction_m = lm_length - spline_length
    reduction_pct = 100 * reduction_m / lm_length

    print("\n--- comparison ---")
    print(f"lawnmower:      {lm_length/1000:.1f} km, {lm_pct:.1f}% coverage")
    print(f"spline offset:  {spline_length/1000:.1f} km, {spline_pct:.1f}% coverage")
    print(f"reduction: {reduction_m/1000:.1f} km ({reduction_pct:.1f}%)")

    return reduction_m, reduction_pct


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="River corridor coverage path planner")
    parser.add_argument("geojson", nargs="?", default="curved_river.geojson",
                         help="river polygon GeoJSON to plan over")
    parser.add_argument("--pixel-size", type=float, default=1.0, help="raster pixel size in meters")
    parser.add_argument("--pad", type=int, default=10, help="raster padding in pixels")
    parser.add_argument("--skip-lawnmower", action="store_true",
                         help="skip the lawnmower baseline and comparison")
    parser.add_argument("--plot", action="store_true", help="plot the resulting paths")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    swath, r_min, offset = get_vehicle_parameters()
    river_polygon = load_river_polygon(args.geojson)

    spline = run_spline_path(river_polygon, args.pixel_size, args.pad, swath, offset, r_min)

    lawnmower = None
    if not args.skip_lawnmower:
        lawnmower = run_lawnmower_baseline(river_polygon, offset, r_min, swath)
        compare_paths(lawnmower, spline)

    if args.plot:
        if lawnmower is not None:
            plot_river_path(river_polygon, lawnmower["path"])
        plot_river_path(river_polygon, spline["flight_path"])
        plot_river_path(river_polygon, spline["simplified_path"])

    return spline, lawnmower


if __name__ == "__main__":
    main()
