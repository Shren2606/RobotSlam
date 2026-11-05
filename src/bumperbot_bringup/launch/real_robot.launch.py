
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

from launch_ros.actions import Node
# Defines ROS 2 nodes to be started by the launch system.


# ============================================================
# ROS 2 PACKAGE MANAGEMENT
# ============================================================

from ament_index_python.packages import get_package_share_directory
# Retrieves the installed share directory of a ROS 2 package.
# Used to locate launch files, configuration files and resources.


# ============================================================
# PACKAGE PATHS
# Lấy đường dẫn thư mục share của các ROS 2 packages.
# Không hardcode đường dẫn tuyệt đối trên Ubuntu.
# ============================================================

FIRMWARE_PKG = "bumperbot_firmware"
CONTROLLER_PKG = "bumperbot_controller"


def get_launch_file(package_name, launch_file):
    """
    Trả về PythonLaunchDescriptionSource của một launch file.

    Args:
        package_name: Tên ROS 2 package chứa launch file.
        launch_file: Tên file .launch.py cần nạp.
    """
    package_path = get_package_share_directory(package_name)

    launch_path = os.path.join(
        package_path,
        "launch",
        launch_file
    )

    return PythonLaunchDescriptionSource(launch_path)


# ============================================================
# MAIN LAUNCH DESCRIPTION
# Khởi chạy toàn bộ hệ thống robot.
# ============================================================

def generate_launch_description():

    # --------------------------------------------------------
    # 1. HARDWARE INTERFACE
    # Kết nối ROS 2 với phần cứng robot.
    # Ví dụ: Motor driver, serial communication...
    # --------------------------------------------------------

    hardware_interface = IncludeLaunchDescription(
        get_launch_file(
            FIRMWARE_PKG,
            "hardware_interface.launch.py"
        )
    )

    # --------------------------------------------------------
    # 2. CONTROLLER
    # Khởi chạy bộ điều khiển chuyển động robot.
    #
    # use_simple_controller = False:
    # Sử dụng controller đầy đủ thay vì simple controller.
    #
    # use_python = False:
    # Sử dụng implementation C++ nếu launch file hỗ trợ.
    # --------------------------------------------------------

    controller = IncludeLaunchDescription(
        get_launch_file(
            CONTROLLER_PKG,
            "controller.launch.py"
        ),
        launch_arguments={
            "use_simple_controller": "False",
            "use_python": "False"
        }.items()
    )

    # --------------------------------------------------------
    # 3. JOYSTICK TELEOPERATION
    # Điều khiển robot bằng tay cầm joystick.
    #
    # use_sim_time = False:
    # Sử dụng thời gian thực từ hệ thống.
    # --------------------------------------------------------

    joystick = IncludeLaunchDescription(
        get_launch_file(
            CONTROLLER_PKG,
            "joystick_teleop.launch.py"
        ),
        launch_arguments={
            "use_sim_time": "False"
        }.items()
    )

    # --------------------------------------------------------
    # 4. IMU DRIVER
    # Khởi chạy node đọc dữ liệu cảm biến MPU6050.
    #
    # Publisher:
    #   Đọc dữ liệu IMU và gửi lên ROS 2 topic.
    # --------------------------------------------------------

    imu_driver_node = Node(
        package=FIRMWARE_PKG,
        executable="mpu6050_driver.py",
        output="screen"
    )

    # --------------------------------------------------------
    # 5. RETURN LAUNCH DESCRIPTION
    # Thứ tự khai báo các thành phần trong hệ thống.
    # --------------------------------------------------------

    return LaunchDescription([
        hardware_interface,
        controller,
        joystick,
        imu_driver_node
    ])
