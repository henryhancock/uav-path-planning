from rdp import rdp
from pyproj import Transformer
import numpy as np


# eventually going to export path as mavlink mission waypoints
def return_to_global(flight_path, out_path, crs_in=26916, crs_out=4326):

    simplified_path = rdp(flight_path, epsilon=1.0) 
    print(f"Reduced waypoints from {len(flight_path)} to {len(simplified_path)}")
    transformer = Transformer.from_crs(crs_in, crs_out, always_xy=True)
    lon, lat = transformer.transform(simplified_path[:, 0], simplified_path[:, 1])
    global_path = np.column_stack([lon, lat])

    np.savetxt(out_path, global_path, delimiter=",", header="lon,lat", comments="")

    return global_path
