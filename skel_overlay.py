import matplotlib.pyplot as plt

def skel_river_overlay(raster_mask, width_along_centerline, longest_path=None, alpha=0.75):
    #alpha = transparency of width overlay

    # Rotate both layers (transpose)
    mask_rot = raster_mask.T
    center_rot = width_along_centerline.T

    plt.figure(figsize=(10, 4))
    plt.imshow(mask_rot, cmap='gray')
    plt.imshow(center_rot, cmap='magma', alpha=alpha)

    # Overlay longest path if provided
    if longest_path is not None and len(longest_path) > 1:
        # Convert (row, col) → rotated coordinates
        xs = [c for r, c in longest_path]
        ys = [r for r, c in longest_path]

        # After transpose: x ← row, y ← col
        xs_rot = ys
        ys_rot = xs

        plt.plot(xs_rot, ys_rot, color='cyan', linewidth=2.5)

    plt.title("Raster Mask + Medial Axis + Longest Path (Rotated)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()
