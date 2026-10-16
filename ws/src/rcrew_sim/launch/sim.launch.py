"""Starts Ignition Gazebo Fortress with a Create 3 + lidar + camera.

Based on irobot_create_ignition_bringup/create3_spawn.launch.py, but with
our robot description and bridges for the extra sensors.

Main ROS topics:
  /cmd_vel                 geometry_msgs/Twist    (input)
  /odom                    nav_msgs/Odometry
  /tf, /tf_static
  /scan                    sensor_msgs/LaserScan
  /camera/image_raw        sensor_msgs/Image
  /camera/camera_info      sensor_msgs/CameraInfo
"""

import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            SetEnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


ROBOT_NAME = 'create3'
# No dock in this world, but the Create 3 bridges/nodes still expect a name.
DOCK_NAME = 'standard_dock'


def generate_launch_description():
    pkg_rcrew = get_package_share_directory('rcrew_sim')
    pkg_bringup = get_package_share_directory('irobot_create_ignition_bringup')
    pkg_plugins = get_package_share_directory('irobot_create_ignition_plugins')
    pkg_common = get_package_share_directory('irobot_create_common_bringup')
    pkg_description = get_package_share_directory('irobot_create_description')
    pkg_ros_ign_gazebo = get_package_share_directory('ros_ign_gazebo')

    world = LaunchConfiguration('world')
    gui = LaunchConfiguration('gui')

    args = [
        DeclareLaunchArgument('world', default_value='room',
                              description='Ignition world: room | depot (must match the <world name>)'),
        DeclareLaunchArgument('gui', default_value='true',
                              choices=['true', 'false'],
                              description='Open the Gazebo GUI'),
    ]

    env = [
        SetEnvironmentVariable(
            'IGN_GAZEBO_RESOURCE_PATH',
            os.path.join(pkg_rcrew, 'worlds') + ':'
            + os.path.join(pkg_bringup, 'worlds') + ':'
            + str(Path(pkg_description).parent.resolve())),
        SetEnvironmentVariable('IGN_GUI_PLUGIN_PATH',
                               os.path.join(pkg_plugins, 'lib')),
    ]

    # -r: start running without pressing play. -s: server only.
    gui_config = os.path.join(pkg_rcrew, 'gui', 'gui.config')
    ign_args = PythonExpression([
        "'", world, ".sdf -r -v 2 ' + ('--gui-config ", gui_config, "' if '",
        gui, "' == 'true' else '-s')"])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_ign_gazebo, 'launch', 'ign_gazebo.launch.py')),
        launch_arguments=[('ign_args', ign_args)])

    robot_description = Command([
        'xacro ', os.path.join(pkg_rcrew, 'urdf', 'create3_rcrew.urdf.xacro'),
        ' gazebo:=ignition namespace:='])

    robot_state_publisher = Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'robot_description': robot_description}])

    joint_state_publisher = Node(
        package='joint_state_publisher', executable='joint_state_publisher',
        output='screen', parameters=[{'use_sim_time': True}])

    spawn_robot = Node(
        package='ros_ign_gazebo', executable='create', output='screen',
        arguments=['-name', ROBOT_NAME, '-topic', 'robot_description',
                   '-x', '0', '-y', '0', '-z', '0', '-Y', '0'])

    clock_bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        name='clock_bridge', output='screen',
        arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'])

    # Stock Create 3 bridges (cmd_vel, odom tf, bumper, cliff, IR, buttons)
    create3_bridges = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bringup, 'launch', 'create3_ros_ignition_bridge.launch.py')),
        launch_arguments=[('world', world), ('robot_name', ROBOT_NAME),
                          ('dock_name', DOCK_NAME)])

    # Nodes emulating the Create 3 firmware (motion control, docking, etc.)
    create3_nodes = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_common, 'launch', 'create3_nodes.launch.py')),
        launch_arguments=[('namespace', '')])

    create3_ignition_nodes = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bringup, 'launch', 'create3_ignition_nodes.launch.py')),
        launch_arguments=[('robot_name', ROBOT_NAME), ('dock_name', DOCK_NAME)])

    sensor_bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        name='sensor_bridge', output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image[ignition.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo',
        ])

    return LaunchDescription(args + env + [
        gazebo,
        clock_bridge,
        robot_state_publisher,
        joint_state_publisher,
        spawn_robot,
        create3_bridges,
        create3_nodes,
        create3_ignition_nodes,
        sensor_bridge,
    ])
