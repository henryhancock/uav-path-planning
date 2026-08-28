import matplotlib.pyplot as plt


def plot_river_path(river_polygon, flight_path, title="River coverage path"):
    fig, ax = plt.subplots(figsize=(10, 8))

    x, y = river_polygon.exterior.xy
    ax.fill(x, y, color="lightblue", alpha=0.5, label="River corridor")
    for interior in river_polygon.interiors:
        ix, iy = interior.xy
        ax.fill(ix, iy, color="white")

    ax.plot(flight_path[:, 0], flight_path[:, 1], color="red", linewidth=1.5, label="Flight path")

    ax.set_aspect("equal")
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
    ax.set_title(title)
    ax.legend()
    plt.show()