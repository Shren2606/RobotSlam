
# ============================================================
# STANDARD PYTHON LIBRARIES
# ============================================================

import os  # Thư viện xử lý đường dẫn file và thư mục


# ============================================================
# ROS 2 LAUNCH LIBRARIES
# ============================================================

from launch import LaunchDescription
# Khai báo danh sách các hành động cần thực hiện khi chạy Launch.

from launch_ros.actions import Node
# Cho phép khởi chạy các ROS 2 Node.

from launch_ros.parameter_descriptions import ParameterValue
# Xác định kiểu dữ liệu của parameter được truyền vào Node.

from launch.substitutions import Command
# Thực thi command và lấy kết quả đầu ra.

from ament_index_python.packages import get_package_share_directory
# Lấy đường dẫn thư mục share của package ROS 2 đã cài đặt.


# ============================================================
# LAUNCH DESCRIPTION
# ============================================================

def generate_launch_description():

    # --------------------------------------------------------
    # ROBOT DESCRIPTION
    # --------------------------------------------------------

    # Xử lý file Xacro để tạo robot_description dạng URDF.
    # is_sim:=False xác định cấu hình robot chạy trên phần cứng thực.
    # Command thực thi lệnh xacro và trả về nội dung URDF.
    robot_description = ParameterValue(
        Command(
            [
                "xacro ",
                os.path.join(
                    # Lấy đường dẫn package bumperbot_description.
                    get_package_share_directory("bumperbot_description"),

                    # Đường dẫn đến thư mục chứa file URDF/Xacro.
                    "urdf",

                    # Tên file mô tả robot.
                    "bumperbot.urdf.xacro",
                ),

                # Truyền argument để lựa chọn cấu hình robot thực.
                " is_sim:=False"
            ]
        ),

        # Chuyển kết quả xử lý Xacro thành kiểu chuỗi.
        value_type=str,
    )


    # --------------------------------------------------------
    # ROBOT STATE PUBLISHER
    # --------------------------------------------------------

    # Khởi chạy robot_state_publisher.
    # Node sử dụng robot_description để xác định cấu trúc robot
    # và publish các transform lên hệ thống TF.
    #ros2 run robot_state_publisher robot_state_publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",

        # Truyền nội dung URDF vào parameter robot_description.
        parameters=[
            {
                "robot_description": robot_description
            }
        ],
    )



    # --------------------------------------------------------
    # ROS 2 CONTROL - CONTROLLER MANAGER
    # --------------------------------------------------------

    # Khởi chạy ros2_control_node.
    # Node chịu trách nhiệm quản lý hardware interface
    # và các controller của robot.
    #ros2 run controller_manager ros2_control_node
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",

        # Truyền các parameter và file cấu hình controller.
        parameters=[

            # Robot description và cấu hình thời gian.
            {
                "robot_description": robot_description,

                # Sử dụng thời gian thực thay vì simulation clock.
                "use_sim_time": False,
            },

            # Lấy đường dẫn đến file YAML cấu hình controller.
            os.path.join(
                get_package_share_directory(
                    "bumperbot_controller"
                ),

                # Thư mục chứa file cấu hình.
                "config",

                # File cấu hình Controller Manager và controller.
                "bumperbot_controllers.yaml",
            ),
        ],
    )


    # --------------------------------------------------------
    # LAUNCH DESCRIPTION
    # --------------------------------------------------------

    # Trả về danh sách Node cần khởi chạy.
    return LaunchDescription(
        [
            # Publish robot description và TF.
            robot_state_publisher_node,

            # Khởi chạy hệ thống ROS 2 Control.
            controller_manager,
        ]
    )
