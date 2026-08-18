This project is developing a coverage path planning algorithm for fixed-wing UAVs surveying rivers. The approach extracts a river centerline from GIS data, generates the coverage passes required by the river width and camera swath, and connects them with Dubins paths that respect the turning radius of the aircraft. Performance is evaluated in simulation by comparing against a lawnmower baseline using real river geometry.

This project does not include wind models, physical testing, navigation, or control.

Vehicle specifications are pulled from the eBee X, a common fixed wing survey UAV.
Minimum turn radius - 20 meters
Operating height - 120 meters
56 degree horizontal FOV - senseFly Aeria X, 