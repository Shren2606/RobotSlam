
# ============================================================
# STANDARD PYTHON LIBRARIES
# ============================================================

import os  # Provides functions for handling file paths and directories


# ============================================================
# ROS 2 LAUNCH LIBRARIES
# ============================================================

from launch import LaunchDescription
# Defines the complete launch configuration for a ROS 2 system.

from launch.actions import IncludeLaunchDescription
# Allows including and executing other launch files.

from launch.launch_description_sources import PythonLaunchDescriptionSource
# Loads ROS 2 launch files written in Python.


# ============================================================
# ROS 2 PACKAGE MANAGEMENT
# ============================================================

from ament_index_python.packages import get_package_share_directory
# Retrieves the installed share directory of a ROS 2 package.


# ============================================================
# PACKAGE CONFIGURATION
# ============================================================

DESCRIPTION_PKG = "bumperbot_description"
CONTROLLER_PKG = "bumperbot_controller"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_launch_file(package_name, launch_file):
    """
    Locate and return a ROS 2 Python launch file.

    Args:
        package_name: Name of the ROS 2 package.
        launch_file: Name of the launch file.

    Returns:
        PythonLaunchDescriptionSource: Launch file source.
    """

    # Get the installed package share directory.
    package_path = get_package_share_directory(package_name)

    # Construct the full path to the launch file.
    launch_path = os.path.join(
        package_path,
        "launch",
        launch_file
    )

    # Return the Python launch file source.
    return PythonLaunchDescriptionSource(launch_path)


# ============================================================
# MAIN LAUNCH DESCRIPTION
# ============================================================

def generate_launch_description():
    """
    Launch the robot simulation with controllers and joystick.

    System components:
        1. Gazebo simulation
        2. Robot controllers
        3. Joystick teleoperation
    """

    # --------------------------------------------------------
    # 1. GAZEBO SIMULATION
    # Start the robot simulation environment.
    # --------------------------------------------------------

    gazebo = IncludeLaunchDescription(
        get_launch_file(
            DESCRIPTION_PKG,
            "gazebo.launch.py"
        )
    )

    # --------------------------------------------------------
    # 2. ROBOT CONTROLLER
    # Start the robot motion control system.
    #
    # use_simple_controller = False:
    # Use the full controller implementation.
    #
    # use_python = False:
    # Use the C++ controller implementation.
    # --------------------------------------------------------

    controller = IncludeLaunchDescription(
        get_launch_file(
            CONTROLLER_PKG,
            "controller.launch.py"
        ),
        launch_arguments={
            "use_simple_controller": "True",
            "use_python": "False"
        }.items()
    )

    # --------------------------------------------------------
    # 3. JOYSTICK TELEOPERATION
    # Enable manual robot control using a joystick.
    #
    # use_sim_time = True:
    # Synchronize ROS time with Gazebo simulation time.
    # --------------------------------------------------------

    joystick = IncludeLaunchDescription(
        get_launch_file(
            CONTROLLER_PKG,
            "joystick_teleop.launch.py"
        ),
        launch_arguments={
            "use_sim_time": "True"
        }.items()
    )

    # --------------------------------------------------------
    # 4. RETURN LAUNCH DESCRIPTION
    # Register all launch components.
    # --------------------------------------------------------

    return LaunchDescription([
        gazebo,
        controller,
        joystick
    ])
