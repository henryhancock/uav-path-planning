import matplotlib.pyplot as plt

def skel_river_overlay(raster_mask, width_along_centerline, longest_path=None, alpha=0.75):
    """Plots the centerline distance map and longest path along the raster mask of the river segment
    args:
    raster_mask : raster mask of river
    width_along_centerline : centerline of river with associated width
    longest_path : the longest path along the centerline. if provided, will be overlaid on the raster mask
    alpha (float) : between 0 and 1. transparency of the overlaid segments.
    
    """
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

    plt.title("Raster Mask + Medial Axis + Longest Path")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig('docs/overlay.png')
    plt.show()
