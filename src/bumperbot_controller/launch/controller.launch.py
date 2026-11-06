
from launch import LaunchDescription

# DeclareLaunchArgument: Khai báo tham số truyền từ terminal
# GroupAction: Nhóm nhiều launch actions
# OpaqueFunction: Thực thi Python function trong quá trình launch
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    OpaqueFunction
)

# Node: Khởi chạy ROS 2 node hoặc executable
from launch_ros.actions import Node

# LaunchConfiguration: Đọc giá trị launch argument
from launch.substitutions import LaunchConfiguration

# UnlessCondition: Chạy action khi điều kiện False
# IfCondition: Chạy action khi điều kiện True
from launch.conditions import UnlessCondition, IfCondition


# ============================================================
# NOISY CONTROLLER FUNCTION
# ============================================================

def noisy_controller(context, *args, **kwargs):

    # --------------------------------------------------------
    # ĐỌC LAUNCH ARGUMENT
    # --------------------------------------------------------

    # Đọc tham số sử dụng simulation time
    use_sim_time = LaunchConfiguration("use_sim_time")

    # Đọc tham số lựa chọn Python hoặc C++
    use_python = LaunchConfiguration("use_python")

    # Đọc bán kính bánh xe và chuyển sang float
    wheel_radius = float(
        LaunchConfiguration("wheel_radius").perform(context)
    )

    # Đọc khoảng cách giữa hai bánh xe
    wheel_separation = float(
        LaunchConfiguration("wheel_separation").perform(context)
    )

    # Đọc sai số bán kính bánh xe
    wheel_radius_error = float(
        LaunchConfiguration("wheel_radius_error").perform(context)
    )

    # Đọc sai số khoảng cách giữa hai bánh xe
    wheel_separation_error = float(
        LaunchConfiguration("wheel_separation_error").perform(context)
    )

    # --------------------------------------------------------
    # PYTHON NOISY CONTROLLER
    # --------------------------------------------------------

    # Khởi chạy noisy_controller.py
    noisy_controller_py = Node(
        package="bumperbot_controller",

        # Executable Python
        executable="noisy_controller.py",

        # Truyền các ROS 2 parameters vào node
        parameters=[
            {
                # Bán kính bánh xe có thêm sai số
                "wheel_radius":
                    wheel_radius + wheel_radius_error,

                # Khoảng cách hai bánh có thêm sai số
                "wheel_separation":
                    wheel_separation + wheel_separation_error,

                # Sử dụng ROS simulation time
                "use_sim_time": use_sim_time
            }
        ],

        # Chỉ chạy node Python khi use_python=True
        condition=IfCondition(use_python),
    )

    # --------------------------------------------------------
    # C++ NOISY CONTROLLER
    # --------------------------------------------------------

    # Khởi chạy noisy_controller C++
    noisy_controller_cpp = Node(
        package="bumperbot_controller",

        # Executable C++
        executable="noisy_controller",

        # Truyền các ROS 2 parameters vào node
        parameters=[
            {
                # Bán kính bánh xe có thêm sai số
                "wheel_radius":
                    wheel_radius + wheel_radius_error,

                # Khoảng cách hai bánh có thêm sai số
                "wheel_separation":
                    wheel_separation + wheel_separation_error,

                # Sử dụng ROS simulation time
                "use_sim_time": use_sim_time
            }
        ],

        # Chỉ chạy C++ khi use_python=False
        condition=UnlessCondition(use_python),
    )

    # Trả về danh sách node để Launch system thực thi
    return [
        noisy_controller_py,
        noisy_controller_cpp,
    ]


# ============================================================
# GENERATE LAUNCH DESCRIPTION
# ============================================================

def generate_launch_description():

    # --------------------------------------------------------
    # 1. DECLARE LAUNCH ARGUMENTS
    # --------------------------------------------------------

    # Khai báo sử dụng simulation time
    # True: Sử dụng thời gian từ simulator /clock
    # False: Sử dụng thời gian thực của hệ thống
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="True",
    )

    # Lựa chọn sử dụng Simple Controller hay DiffDrive Controller
    # True: Simple Controller
    # False: DiffDrive Controller
    use_simple_controller_arg = DeclareLaunchArgument(
        "use_simple_controller",
        default_value="True",
    )

    # Lựa chọn controller viết bằng Python hay C++
    # True: Python
    # False: C++
    use_python_arg = DeclareLaunchArgument(
        "use_python",
        default_value="False",
    )

    # Khai báo bán kính bánh xe mặc định (m)
    wheel_radius_arg = DeclareLaunchArgument(
        "wheel_radius",
        default_value="0.033",
    )

    # Khai báo khoảng cách hai bánh xe mặc định (m)
    wheel_separation_arg = DeclareLaunchArgument(
        "wheel_separation",
        default_value="0.17",
    )

    # Khai báo sai số bán kính bánh xe (m)
    wheel_radius_error_arg = DeclareLaunchArgument(
        "wheel_radius_error",
        default_value="0.005",
    )

    # Khai báo sai số khoảng cách hai bánh xe (m)
    wheel_separation_error_arg = DeclareLaunchArgument(
        "wheel_separation_error",
        default_value="0.02",
    )

    # --------------------------------------------------------
    # 2. LOAD LAUNCH CONFIGURATIONS
    # --------------------------------------------------------

    # Đọc giá trị các launch arguments
    use_sim_time = LaunchConfiguration("use_sim_time")

    use_simple_controller = LaunchConfiguration(
        "use_simple_controller"
    )

    use_python = LaunchConfiguration("use_python")

    wheel_radius = LaunchConfiguration("wheel_radius")

    wheel_separation = LaunchConfiguration(
        "wheel_separation"
    )

    # --------------------------------------------------------
    # 3. JOINT STATE BROADCASTER SPAWNER
    # --------------------------------------------------------

    # Gọi controller_manager spawner để load và activate
    # joint_state_broadcaster
    #
    # Controller này publish trạng thái các joints
    # lên topic /joint_states

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",

        # Executable spawner
        executable="spawner",

        # Tên controller cần spawn
        # Controller manager cần kết nối
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    # --------------------------------------------------------
    # 4. DIFF DRIVE CONTROLLER SPAWNER
    # --------------------------------------------------------

    # Gọi controller_manager để load DiffDrive Controller
    #
    # Controller này nhận cmd_vel và điều khiển hai bánh
    # đồng thời tính toán odometry
    wheel_controller_spawner = Node(
        package="controller_manager",

        executable="spawner",

        arguments=[
            "bumperbot_controller",
            "--controller-manager",
            "/controller_manager"
        ],

        # Chỉ chạy khi use_simple_controller=False
        condition=UnlessCondition(use_simple_controller),
    )

    # --------------------------------------------------------
    # 5. SIMPLE CONTROLLER GROUP
    # --------------------------------------------------------

    # GroupAction: Gom nhiều action vào một nhóm
    #
    # Khi use_simple_controller=True:
    #   1. Spawn simple_velocity_controller
    #   2. Chạy simple_controller Python hoặc C++
    #
    # Khi False: Không chạy toàn bộ nhóm này

    simple_controller = GroupAction(

        # Chỉ chạy group khi sử dụng Simple Controller
        condition=IfCondition(use_simple_controller),

        actions=[

            # ------------------------------------------------
            # 5.1 SPAWN SIMPLE VELOCITY CONTROLLER
            # ------------------------------------------------

            # Controller này nhận lệnh vận tốc bánh xe
            # và gửi xuống hardware interface
            Node(
                package="controller_manager",

                executable="spawner",

                arguments=[
                    "simple_velocity_controller",
                    "--controller-manager",
                    "/controller_manager"
                ]
            ),

            # ------------------------------------------------
            # 5.2 SIMPLE CONTROLLER PYTHON
            # ------------------------------------------------

            # Node Python tính động học bánh xe và odometry
            Node(
                package="bumperbot_controller",

                executable="simple_controller.py",

                # Truyền parameters cho node
                parameters=[
                    {
                        # Bán kính bánh xe
                        "wheel_radius": wheel_radius,

                        # Khoảng cách hai bánh xe
                        "wheel_separation": wheel_separation,

                        # Sử dụng simulation time
                        "use_sim_time": use_sim_time
                    }
                ],

                # Chỉ chạy khi use_python=True
                condition=IfCondition(use_python),
            ),

            # ------------------------------------------------
            # 5.3 SIMPLE CONTROLLER C++
            # ------------------------------------------------

            # Node C++ có chức năng tương tự Python controller
            Node(
                package="bumperbot_controller",

                executable="simple_controller",

                # Truyền parameters cho node
                parameters=[
                    {
                        "wheel_radius": wheel_radius,
                        "wheel_separation": wheel_separation,
                        "use_sim_time": use_sim_time
                    }
                ],

                # Chỉ chạy khi use_python=False
                condition=UnlessCondition(use_python),
            ),
        ]
    )

    # --------------------------------------------------------
    # 6. NOISY CONTROLLER LAUNCH
    # --------------------------------------------------------

    # OpaqueFunction:
    # Gọi noisy_controller() trong quá trình launch
    #
    # Hàm này tính toán thông số bánh xe có sai số
    # rồi lựa chọn chạy Python hoặc C++

    noisy_controller_launch = OpaqueFunction(
        function=noisy_controller
    )

    # --------------------------------------------------------
    # 7. RETURN LAUNCH DESCRIPTION
    # --------------------------------------------------------

    # Danh sách tất cả actions cần thực thi
    return LaunchDescription(
        [
            # Launch arguments
            use_sim_time_arg,
            use_simple_controller_arg,
            use_python_arg,
            wheel_radius_arg,
            wheel_separation_arg,
            wheel_radius_error_arg,
            wheel_separation_error_arg,

            # Controllers
            joint_state_broadcaster_spawner,
            wheel_controller_spawner,
            simple_controller,

            # Noisy controller
            noisy_controller_launch,
        ]
    )
