
# ============================================================
# IMPORT LIBRARIES
# ============================================================

# Thư viện xử lý đường dẫn file và thư mục
import os

# Lấy đường dẫn thư mục share của một ROS 2 package đã cài đặt
from ament_index_python.packages import get_package_share_directory

# LaunchDescription: Mô tả danh sách các action cần thực thi
from launch import LaunchDescription

# DeclareLaunchArgument: Khai báo tham số truyền vào Launch File
from launch.actions import DeclareLaunchArgument

# LaunchConfiguration: Đọc giá trị Launch Argument
from launch.substitutions import LaunchConfiguration

# Node: Khởi chạy ROS 2 Node
from launch_ros.actions import Node


# ============================================================
# GENERATE LAUNCH DESCRIPTION
# ============================================================

def generate_launch_description():

    # --------------------------------------------------------
    # 1. DECLARE LAUNCH ARGUMENT
    # --------------------------------------------------------

    # Khai báo tham số use_sim_time
    #
    # True:
    # Sử dụng thời gian từ simulator /clock
    #
    # False:
    # Sử dụng thời gian thực của hệ thống
    #
    # description:
    # Mô tả tham số khi người dùng xem thông tin Launch File

    use_sim_time_arg = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="True",
        description="Use simulated time"
    )

    # --------------------------------------------------------
    # 2. JOY TELEOP NODE
    # --------------------------------------------------------

    # Node joy_teleop:
    # Chuyển đổi dữ liệu joystick thành lệnh vận tốc robot
    #
    # Input:
    # /joy
    #
    # Output:
    # /cmd_vel hoặc topic được khai báo trong joy_teleop.yaml
    #
    # File cấu hình:
    # bumperbot_controller/config/joy_teleop.yaml

    joy_teleop = Node(

        # ROS 2 package chứa executable
        package="joy_teleop",

        # Tên executable cần chạy
        executable="joy_teleop",

        # Truyền các parameters vào Node
        parameters=[

            # Đọc file cấu hình joystick teleoperation
            os.path.join(
                get_package_share_directory(
                    "bumperbot_controller"
                ),
                "config",
                "joy_teleop.yaml"
            ),

            # Truyền tham số sử dụng simulation time
            {
                "use_sim_time":
                    LaunchConfiguration("use_sim_time")
            }
        ]
    )

    # --------------------------------------------------------
    # 3. JOY LINUX NODE
    # --------------------------------------------------------

    # Node joy_linux:
    # Đọc dữ liệu trực tiếp từ joystick được kết nối với Linux
    #
    # Input:
    # USB Joystick / Gamepad
    #
    # Output:
    # Topic /joy
    #
    # File cấu hình:
    # bumperbot_controller/config/joy_config.yaml

    joy_node = Node(

        # ROS 2 package đọc joystick trên Linux
        package="joy",

        # Executable đọc dữ liệu joystick
        executable="joy_node",

        # Đặt tên Node là joystick
        name="joystick",

        # Truyền các parameters vào Node
        parameters=[

            # Đọc file cấu hình joystick
            os.path.join(
                get_package_share_directory(
                    "bumperbot_controller"
                ),
                "config",
                "joy_config.yaml"
            ),

            # Sử dụng simulation time
            {
                "use_sim_time":
                    LaunchConfiguration("use_sim_time")
            }
        ]
    )

    # --------------------------------------------------------
    # 4. RETURN LAUNCH DESCRIPTION
    # --------------------------------------------------------

    # Trả về danh sách các action cần chạy
    return LaunchDescription(
        [
            # Khai báo tham số use_sim_time
            use_sim_time_arg,

            # Khởi chạy node chuyển joystick thành lệnh vận tốc
            joy_teleop,

            # Khởi chạy node đọc joystick từ thiết bị Linux
            joy_node
        ]
    )


