import numpy as np
import matplotlib.pyplot as plt
from pyproj import Transformer

PLANNED_CSV = "waypoints.csv"
FLOWN_CSV = "flown_path.csv"
SPEED_FACTOR = 5.0      # PX4_SIM_SPEED_FACTOR used for the flight (1.0 if real time)
TRIM_RADIUS = 20.0      # meters; mission window starts/ends when within this of first/last waypoint
CHUNK = 5000            # flown points processed per batch

print("debug debug debug this has started running!!!")
def to_utm(lon, lat):
    transformer = Transformer.from_crs(4326, 26916, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return np.column_stack([x, y])


def distance_to_path(points, path):
    """Unsigned distance from each point to the nearest segment of a polyline."""
    a = path[:-1]
    d = path[1:] - a
    seg_len2 = np.maximum(np.sum(d**2, axis=1), 1e-12)

    out = np.empty(len(points))
    for i in range(0, len(points), CHUNK):
        p = points[i:i + CHUNK, None, :]                                  # (k, 1, 2)
        s = np.clip(np.sum((p - a) * d, axis=2) / seg_len2, 0.0, 1.0)    # (k, m)
        proj = a + s[..., None] * d                                       # (k, m, 2)
        out[i:i + CHUNK] = np.min(np.linalg.norm(p - proj, axis=2), axis=1)
    return out


planned_ll = np.loadtxt(PLANNED_CSV, delimiter=",", skiprows=1)          # lon, lat
flown_raw = np.loadtxt(FLOWN_CSV, delimiter=",", skiprows=1)             # t_wall_s, lat, lon, rel_alt_m

planned = to_utm(planned_ll[:, 0], planned_ll[:, 1])
flown = to_utm(flown_raw[:, 2], flown_raw[:, 1])
t = flown_raw[:, 0] * SPEED_FACTOR

# Trim takeoff/climb-out and the RTL leg: keep from first arrival at waypoint 1 to last arrival at the final waypoint
near_start = np.where(np.linalg.norm(flown - planned[1], axis=1) < TRIM_RADIUS)[0]
near_end = np.where(np.linalg.norm(flown - planned[-1], axis=1) < TRIM_RADIUS)[0]
i0 = near_start[0] if len(near_start) else 0
i1 = near_end[-1] + 1 if len(near_end) else len(flown)

flown_m = flown[i0:i1]
t_m = t[i0:i1] - t[i0]
err = distance_to_path(flown_m, planned)

print(f"points analyzed: {len(err)} of {len(flown)}")
print(f"mission time:    {t_m[-1]:.0f} s")
print(f"mean error:      {err.mean():.2f} m")
print(f"RMS error:       {np.sqrt(np.mean(err**2)):.2f} m")
print(f"95th pct error:  {np.percentile(err, 95):.2f} m")
print(f"peak error:      {err.max():.2f} m at t = {t_m[err.argmax()]:.0f} s")

fig1, ax1 = plt.subplots(figsize=(8, 8))
ax1.plot(planned[:, 0], planned[:, 1], "b-", lw=1.5, label="planned")
ax1.plot(flown_m[:, 0], flown_m[:, 1], "r-", lw=1, label="flown")
ax1.set_aspect("equal")
ax1.set_xlabel("easting (m)")
ax1.set_ylabel("northing (m)")
ax1.set_title("Planned vs flown path")
ax1.legend()
fig1.tight_layout()
fig1.savefig("flown_vs_planned.png", dpi=200)

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(t_m, err, "k-", lw=0.8)
ax2.axhline(np.sqrt(np.mean(err**2)), color="r", ls="--", label="RMS")
ax2.set_xlabel("time since waypoint 1 (s)")
ax2.set_ylabel("cross-track error (m)")
ax2.set_title("Tracking error e(t)")
ax2.legend()
fig2.tight_layout()
fig2.savefig("tracking_error.png", dpi=200)

plt.show()