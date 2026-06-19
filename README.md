# diff_robot

A differential drive robot simulation in ROS2 Jazzy + Gazebo Harmonic.

## Features
- Flat cylinder chassis with two drive wheels and a skid plate
- PID-based navigation controller with a target publisher
- Diff drive plugin with odometry and TF publishing
- ROS2-Gazebo bridge configuration (YAML file, added in launch arguements)

## Dependencies
- ROS2 Jazzy
- Gazebo Harmonic
- ros-jazzy-ros-gz-bridge

## Build
```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## Launch
```bash
ros2 launch diff_robot diff_robot.launch.py
```
## Run
```bash
# In a second terminal
ros2 run diff_robot diff_PID.py

# In a third terminal
ros2 run diff_robot diff_target.py
```

## Package Structure
- `urdf/` — robot description
- `launch/` — launch files
- `scripts/` — PID controller,a simple controller and target publisher nodes
- `config/` — Gazebo bridge configuration
