"""Open Gazebo with the obstacle room and spawn the ROSMASTER A1.

What this file starts:
  1. Gazebo (gzserver + gzclient) with worlds/obstacle_room.world
  2. robot_state_publisher, which shares the robot's shape (URDF) on /robot_description
  3. spawn_entity, which puts the robot into the Gazebo world

Options:
  ros2 launch rosmaster_sim sim.launch.py gui:=false     # no Gazebo window
  ros2 launch rosmaster_sim sim.launch.py x:=0.0 y:=0.0  # start somewhere else
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('rosmaster_sim')
    world = os.path.join(pkg, 'worlds', 'obstacle_room.world')
    xacro_file = os.path.join(pkg, 'urdf', 'rosmaster_a1.urdf.xacro')

    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': world, 'gui': LaunchConfiguration('gui')}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
        output='screen',
    )

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'rosmaster_a1',
                   '-x', LaunchConfiguration('x'), '-y', LaunchConfiguration('y'),
                   '-z', '0.02', '-Y', LaunchConfiguration('yaw')],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true', description='Show the Gazebo window'),
        DeclareLaunchArgument('x', default_value='-1.8'),
        DeclareLaunchArgument('y', default_value='-1.8'),
        DeclareLaunchArgument('yaw', default_value='0.785'),
        gazebo,
        robot_state_publisher,
        spawn_robot,
    ])
