import asyncio
import csv
import time
import numpy as np
import matplotlib.pyplot as plt
from rdp import rdp
from pyproj import Transformer
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

from main import get_vehicle_parameters, run_spline_path
from preprocessor import load_river_polygon


# home [-88.3163409   41.91618079]

# make px4_sitl gz_rc_cessna

# various run commands.....

#default w/ gazebo
# cd ~/PX4-Autopilot && export PX4_HOME_LAT=41.91618079 PX4_HOME_LON=-88.3163409 PX4_HOME_ALT=205 && make px4_sitl gz_rc_cessna

#no gazebo, 10x speed, the good one!
# cd ~/PX4-Autopilot && export PX4_HOME_LAT=41.91618079 PX4_HOME_LON=-88.3163409 PX4_HOME_ALT=205 PX4_SIM_SPEED_FACTOR=10 HEADLESS=1 && make px4_sitl gz_rc_cessna

# same as above but added wind...
# cd ~/PX4-Autopilot && export PX4_HOME_LAT=41.91618079 PX4_HOME_LON=-88.3163409 PX4_HOME_ALT=205 PX4_SIM_SPEED_FACTOR=15 HEADLESS=1 PX4_GZ_WORLD=windy && make px4_sitl gz_rc_cessna
# 5x speed, yes gazbeo
# cd ~/PX4-Autopilot && export PX4_HOME_LAT=41.91618079 PX4_HOME_LON=-88.3163409 PX4_HOME_ALT=205 PX4_SIM_SPEED_FACTOR=5 && make px4_sitl gz_rc_cessna

#open QGC
# cd ~ 
# ./QGroundControl-x86_64.AppImage


VELOCITY = 15.0              # cruise speed (meters per second)
AGL = 120.0                  # altitude (meters above ground level)
ACCEPTED_RADIUS = 20.0       # acceptable radius around point to be considered a hit

def return_to_global(flight_path, out_path, crs_in=26916, crs_out=4326):
    """
    Simplifies local UTM coordinates using RDP and transforms them
    into WGS84 (latitude/longitude) global coordinate systems.
    """
    reduced_path = rdp(flight_path, epsilon=1.0)

    transformer = Transformer.from_crs(crs_in, crs_out, always_xy=True)
    lon, lat = transformer.transform(reduced_path[:, 0], reduced_path[:, 1])
    global_path = np.column_stack([lon, lat])

    np.savetxt(out_path, global_path, delimiter=",", header="lon,lat", comments="")

    return global_path


def build_flight_path(geojson_path="curved_river.geojson", pixel_size=1.0, pad=10):
    swath, r_min, offset = get_vehicle_parameters()
    river_polygon = load_river_polygon(geojson_path)
    return run_spline_path(river_polygon, pixel_size, pad, swath, offset, r_min)["flight_path"]


coord_list = return_to_global(build_flight_path(), "waypoints.csv")


async def log_and_plot(drone, out_path="flown_path.csv"):
    """
    Logs the aircraft's position to CSV and live-plots flown vs planned path in UTM meters.
    Note: t_wall_s is wall-clock time; with PX4_SIM_SPEED_FACTOR > 1, use the ULog for sim time.
    """
    to_utm = Transformer.from_crs(4326, 26916, always_xy=True)
    planned_x, planned_y = to_utm.transform(coord_list[:, 0], coord_list[:, 1])

    plt.ion()
    fig, ax = plt.subplots()
    ax.plot(planned_x, planned_y, "b-", label="planned")
    flown_line, = ax.plot([], [], "r-", label="flown")
    ax.set_aspect("equal")
    ax.set_xlabel("easting (m)")
    ax.set_ylabel("northing (m)")
    ax.legend()
    plt.pause(0.001)

    flown_x, flown_y = [], []
    t0 = time.monotonic()
    last_draw = 0.0

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["t_wall_s", "lat", "lon", "rel_alt_m"])

        async for pos in drone.telemetry.position():
            t = time.monotonic() - t0
            writer.writerow([t, pos.latitude_deg, pos.longitude_deg, pos.relative_altitude_m])

            x, y = to_utm.transform(pos.longitude_deg, pos.latitude_deg)
            flown_x.append(x)
            flown_y.append(y)

            # Redraw at most twice a second so plotting doesn't starve the MAVLink loop
            if t - last_draw > 0.5:
                flown_line.set_data(flown_x, flown_y)
                ax.relim()
                ax.autoscale_view()
                plt.pause(0.001)
                f.flush()
                last_draw = t


async def run():
    drone = System()

    # Connect to SITL (default UDP port is 14540)
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected to PX4 SITL!")
            break

    print(f"Processing {len(coord_list)} waypoints...")
    mission_items = []

    for index, (lon, lat) in enumerate(coord_list):
        if index == 0:
            action = MissionItem.VehicleAction.TAKEOFF # need to takeoff first...
        else:
            action = MissionItem.VehicleAction.NONE # only takeoff once

        mission_items.append(
            MissionItem(
                latitude_deg=lat,
                longitude_deg=lon,
                relative_altitude_m=AGL,
                speed_m_s=VELOCITY,
                is_fly_through=True,
                gimbal_pitch_deg=0.0,
                gimbal_yaw_deg=0.0,
                camera_action=MissionItem.CameraAction.NONE,
                loiter_time_s=0.0,
                camera_photo_interval_s=0.0,
                acceptance_radius_m=ACCEPTED_RADIUS,
                yaw_deg=0.0,
                camera_photo_distance_m=0.0,
                vehicle_action=action,
            )
        )

    mission_plan = MissionPlan(mission_items)

    print(f"Uploading batch mission of {len(mission_items)} items to PX4 SITL...")
    await drone.mission.upload_mission(mission_plan)
    print("Upload complete!")

    await drone.mission.set_return_to_launch_after_mission(True)

    print("Overriding catapult parameters for Runway Takeoff Mode...")
    # 1 forces a runway takeoff run instead of waiting for a manual catapult throw
    await drone.param.set_param_int("RWTO_TKOFF", 1)
    await drone.param.set_param_int("COM_RC_IN_MODE", 4)  # Disable manual control
    await drone.param.set_param_int("MIS_TKO_LAND_REQ", 0)
    await drone.param.set_param_int("NAV_DLL_ACT", 0)  # No failsafe on GCS link loss
    await drone.param.set_param_int("COM_LOW_BAT_ACT", 0)  # No failsafe on sim battery drain

    print("Arming flight systems...")
    print("Waiting for global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("Position estimate ready.")
            break

    # start before flight to get takeoff
    logger = asyncio.create_task(log_and_plot(drone))

    print("Arming flight systems...")
    await drone.action.arm()

    print("Starting mission loop - launching aircraft!")
    await drone.mission.start_mission()

    # Keep the script alive until the mission finishes
    async for progress in drone.mission.mission_progress():
        print(f"Mission progress: {progress.current}/{progress.total}")
        if progress.current == progress.total:
            print("Mission complete.")
            break

    logger.cancel()
    try:
        await logger
    except asyncio.CancelledError:
        pass

    print("Flown path saved to flown_path.csv")
    plt.ioff()
    plt.show()  # keep plot open

if __name__ == "__main__":
    asyncio.run(run())