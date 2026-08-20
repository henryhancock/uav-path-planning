"""One-call plotting for the river path planning pipeline.

    from river_plots import plot_all
    plot_all(raster_mask, distance_map, skel_line, long_skel, tck)

Writes numbered PNGs into outdir. Comment out any block you don't want.
Note: skeleton points and spline outputs are (row, col); imshow wants
col on the x axis, hence the [:,1] / [:,0] ordering in every call.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import splev


def plot_all(raster_mask, distance_map, skel_line, long_skel, tck,
             width_along_centerline=None, min_radius=39.7, swath=127.6,
             outdir="figures", n=4000, dpi=150):

    os.makedirs(outdir, exist_ok=True)
    skel = np.asarray(long_skel, dtype=float)

    u = np.linspace(0, 1, n)
    r, c = splev(u, tck)
    d1r, d1c = splev(u, tck, der=1)
    d2r, d2c = splev(u, tck, der=2)
    kappa = np.abs(d1r*d2c - d1c*d2r) / np.maximum((d1r**2 + d1c**2)**1.5, 1e-12)
    radius = 1 / np.maximum(kappa, 1e-12)
    bad = radius < min_radius
    s = np.concatenate(([0], np.cumsum(np.hypot(np.diff(r), np.diff(c)))))

    def save(name):
        plt.axis("off") if "profile" not in name else None
        plt.tight_layout()
        plt.savefig(f"{outdir}/{name}.png", dpi=dpi, bbox_inches="tight")
        plt.close()
        print(f"  {outdir}/{name}.png")

    # 1. raster mask
    plt.figure(figsize=(14, 7)); plt.imshow(raster_mask, cmap="gray")
    plt.title("Rasterized river polygon"); save("01_raster")

    # 2. distance transform
    plt.figure(figsize=(14, 7)); plt.imshow(distance_map, cmap="viridis")
    plt.colorbar(shrink=0.7, label="distance to bank (m)")
    plt.title("Distance transform"); save("02_distance")

    # 3. skeleton: all branches vs extracted longest path
    rows, cols = np.nonzero(skel_line)
    plt.figure(figsize=(14, 7)); plt.imshow(raster_mask, cmap="gray")
    plt.plot(cols, rows, ".", color="tab:blue", ms=1, alpha=.5)
    plt.plot(skel[:, 1], skel[:, 0], ".", color="crimson", ms=1.5)
    plt.title("Medial axis (blue) and longest path (red)"); save("03_skeleton")

    # 4. spline fit -- should hug meanders without chording across them
    plt.figure(figsize=(14, 7)); plt.imshow(raster_mask, cmap="gray")
    plt.plot(skel[:, 1], skel[:, 0], ".", color="tab:blue", ms=1, alpha=.5)
    plt.plot(c, r, "-", color="lime", lw=1.6)
    plt.title("Spline fit over skeleton"); save("04_spline")

    # 5. bends tighter than the aircraft can fly
    plt.figure(figsize=(14, 7)); plt.imshow(raster_mask, cmap="gray")
    plt.plot(c, r, "-", color="0.4", lw=1.2)
    plt.plot(c[bad], r[bad], ".", color="crimson", ms=5)
    plt.title(f"{100*bad.mean():.1f}% below {min_radius:.0f} m turn radius")
    save("05_infeasible")

    # 6. turn radius along the river -- spiky everywhere = smoothing too low
    plt.figure(figsize=(14, 4)); plt.semilogy(s, radius, lw=.8)
    plt.axhline(min_radius, color="crimson", ls="--")
    plt.xlabel("distance along centerline (m)"); plt.ylabel("radius (m)")
    plt.title("Turn radius demanded by the corridor"); plt.grid(alpha=.3)
    save("06_radius_profile")

    # 7. channel width (needs width_along_centerline)
    if width_along_centerline is not None:
        idx = skel.astype(int)
        w = 2 * width_along_centerline[idx[:, 0], idx[:, 1]]
        wide = w > swath
        plt.figure(figsize=(14, 7)); plt.imshow(raster_mask, cmap="gray")
        plt.scatter(skel[:, 1], skel[:, 0], c=w, s=3, cmap="viridis")
        plt.colorbar(shrink=0.7, label="width (m)")
        if wide.any():
            plt.plot(skel[wide, 1], skel[wide, 0], ".", color="crimson", ms=5)
        plt.title(f"Width {w.min():.0f}-{w.max():.0f} m, "
                  f"{100*wide.mean():.1f}% exceed {swath:.0f} m swath")
        save("07_width")