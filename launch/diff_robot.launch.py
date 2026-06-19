#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    pkg_name = 'diff_robot'
    pkg_share = get_package_share_directory(pkg_name)

    # Path to your URDF file
    urdf_file = os.path.join(pkg_share, 'urdf', 'diff_robot.urdf')

    # Read the URDF XML data
    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # 1. Node: robot_state_publisher (Broadcasts /robot_description)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )

    # 2. Node: RViz2 (Visualization)
    #Removed

    # 3. Include: Modern Gazebo Harmonic Simulator Starter
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
        )]),
        # Opens the simulator running an empty world layout immediately (-r) ,-p for paused state
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # 4. Node: Spawner (Reads from the /robot_description topic and builds it in Gazebo)
    spawn_robot_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'my_robot',
            '-topic', 'robot_description',
            '-z', '0.1', # (Spawn ~ 10cm above ground to prevent clipping floor physics)
            '-x', '2',  
            '-y', '2'   
        ],
        output='screen'
    )
    Bridge_node=Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    parameters=[{'config_file': os.path.join(pkg_share, 'config', 'gz_bridge.yaml')}],
    #I didnt really understand the config and parameters
    output='screen'
)

    # Return the entire system execution stack
    return LaunchDescription([
        robot_state_publisher_node,
        gazebo_launch,
        spawn_robot_node,
        Bridge_node
    ])