# Real Robot Launch

## 1. Overview

Launch file `real_robot.launch.py` được sử dụng để khởi chạy hệ thống ROS 2 cho robot Bumperbot trên phần cứng thực.

File Launch thực hiện các nhiệm vụ:

- Xử lý file Xacro để tạo mô tả robot URDF.
- Khởi chạy `robot_state_publisher` để publish robot transforms.
- Khởi chạy `ros2_control_node` để quản lý hệ thống điều khiển robot.
- Nạp cấu hình controller từ file YAML.
- Thiết lập chế độ sử dụng thời gian thực.

## 2. Dependencies

Các package ROS 2 cần thiết:

| Package | Description |
|---|---|
| `bumperbot_description` | Chứa mô tả robot URDF/Xacro |
| `bumperbot_controller` | Chứa cấu hình ROS 2 Control |
| `robot_state_publisher` | Publish robot transforms |
| `controller_manager` | Quản lý hardware interface và controller |
| `ros2_control` | Framework điều khiển robot |
| `ros2_controllers` | Các controller sử dụng cho robot |

## 3. Robot Description

Robot description được tạo từ file:

`bumperbot_description/urdf/bumperbot.urdf.xacro`

Launch sử dụng command:

```bash
xacro bumperbot.urdf.xacro is_sim:=False
```

Argument `is_sim:=False` lựa chọn cấu hình dành cho robot thực.

Kết quả xử lý Xacro được chuyển thành parameter `robot_description` và sử dụng bởi các node trong hệ thống.

## 4. Robot State Publisher

Node:

```text
Package: robot_state_publisher
Executable: robot_state_publisher
```

Chức năng:

- Đọc cấu trúc robot từ URDF.
- Nhận dữ liệu trạng thái joint.
- Tính toán transform giữa các frame.
- Publish transform lên `/tf` và `/tf_static`.

Node này hỗ trợ hiển thị robot trên RViz và cung cấp hệ thống tọa độ cho các node ROS 2 khác.

## 5. Controller Manager

Node:

```text
Package: controller_manager
Executable: ros2_control_node
```

Controller Manager chịu trách nhiệm:

- Khởi tạo ROS 2 Control.
- Đọc robot description và hardware interface.
- Quản lý các controller.
- Thực hiện chu kỳ cập nhật controller.
- Giao tiếp với hardware interface của robot.

### Controller Configuration

File cấu hình:

`bumperbot_controller/config/bumperbot_controllers.yaml`

File YAML chứa các thông số như:

- `update_rate`: Tần số cập nhật controller.
- `bumperbot_controller`: Differential Drive Controller.
- `joint_state_broadcaster`: Publish joint states.
- `simple_velocity_controller`: Điều khiển vận tốc các joint.

## 6. Launch Execution

Khởi chạy robot thực:

```bash
ros2 launch bumperbot_bringup real_robot.launch.py
```

Kiểm tra các node:

```bash
ros2 node list
```

Kiểm tra TF:

```bash
ros2 topic echo /tf
```

Kiểm tra joint states:

```bash
ros2 topic echo /joint_states
```

Kiểm tra controller:

```bash
ros2 control list_controllers
```

## 7. System Architecture

```text
real_robot.launch.py
        |
        +-- Xacro Processing
        |       |
        |       +-- is_sim:=False
        |       |
        |       +-- robot_description
        |
        +-- robot_state_publisher
        |       |
        |       +-- /tf
        |       +-- /tf_static
        |
        +-- ros2_control_node
                |
                +-- Controller Manager
                |
                +-- Hardware Interface
                |
                +-- Controllers
```

## 8. Notes

- Robot description được sử dụng chung bởi `robot_state_publisher` và `ros2_control_node`.
- `use_sim_time=False` sử dụng thời gian thực.
- Controller Manager cần hardware interface tương ứng được khai báo trong URDF.
- Các controller cần được load và activate thông qua `spawner` nếu chưa được khởi chạy bởi Launch hoặc một cơ chế khác.
- Hardware interface phải được cấu hình phù hợp với phần cứng thực tế của robot.

## 9. Important Concepts & Package Roles

### 9.1. Why Are These Packages Required?

Launch file `real_robot.launch.py` sử dụng nhiều package khác nhau để khởi tạo hệ thống robot. Mỗi package đảm nhận một chức năng riêng, từ mô tả cấu trúc robot đến quản lý hệ thống điều khiển phần cứng.

#### 1. `robot_state_publisher`

**Purpose:** Publish robot transforms based on URDF and joint states.

Package này đọc mô hình robot từ parameter `robot_description` và kết hợp với dữ liệu `/joint_states` để tính toán vị trí, hướng của các Link trong hệ thống tọa độ TF.

**Why is it needed?**

- Cung cấp thông tin tọa độ giữa các bộ phận robot.
- Hỗ trợ hiển thị mô hình robot trên RViz.
- Cung cấp TF cho các hệ thống khác như Navigation, SLAM và Sensor Integration.

Nếu không sử dụng package này, các transform từ URDF sẽ không được tự động publish.

#### 2. `controller_manager`

**Purpose:** Manage controllers and hardware components in ROS 2 Control.

Package này cung cấp executable `ros2_control_node`, chịu trách nhiệm quản lý vòng đời controller, hardware interface và chu kỳ cập nhật hệ thống điều khiển.

**Why is it needed?**

- Quản lý các controller của robot.
- Kết nối controller với hardware interface.
- Điều phối việc đọc trạng thái phần cứng và ghi lệnh điều khiển.
- Quản lý trạng thái hoạt động của controller.

Nếu sử dụng ROS 2 Control nhưng không có Controller Manager, hệ thống không có thành phần quản lý và thực thi các controller theo kiến trúc này.

#### 3. `bumperbot_description`

**Purpose:** Provide the robot model and description.

Package này chứa các file URDF/Xacro mô tả cấu trúc robot.

Các thông tin thường bao gồm:

- Link và Joint.
- Hình dạng và kích thước robot.
- Quan hệ giữa các bộ phận.
- Hardware Interface.
- Cấu hình dành cho Simulation hoặc Real Robot.

Launch file sử dụng Xacro để tạo parameter `robot_description`, sau đó truyền cho các node cần thông tin mô tả robot.

**Important:** URDF/Xacro không trực tiếp điều khiển động cơ. Nó mô tả cấu trúc robot và các giao diện phần cứng được khai báo.

#### 4. `bumperbot_controller`

**Purpose:** Provide controller configuration.

Package này chứa file `bumperbot_controllers.yaml`, định nghĩa các controller và thông số hoạt động của chúng.

Ví dụ:

- `DiffDriveController`: Điều khiển robot Differential Drive.
- `JointStateBroadcaster`: Publish trạng thái các joint.
- `JointGroupVelocityController`: Điều khiển vận tốc của một nhóm joint.

File YAML được truyền vào `ros2_control_node` thông qua tham số `parameters`.

**Important:** File YAML chỉ khai báo cấu hình controller. Controller vẫn cần được load và activate thông qua Controller Manager.

### 9.2. Relationship Between Packages

Các package phối hợp với nhau để hình thành hệ thống robot:

| Package | Main Responsibility |
|---|---|
| `bumperbot_description` | Cung cấp mô hình robot |
| `robot_state_publisher` | Publish robot transforms |
| `controller_manager` | Quản lý hệ thống điều khiển |
| `bumperbot_controller` | Cung cấp cấu hình controller |

`robot_state_publisher` và `controller_manager` là hai node độc lập. Chúng cùng sử dụng robot description nhưng đảm nhận hai nhiệm vụ khác nhau:

- Robot State Publisher: Xác định cấu trúc và transform của robot.
- Controller Manager: Quản lý quá trình điều khiển và giao tiếp với phần cứng.

### 9.3. Important Notes

1. `robot_state_publisher` không trực tiếp điều khiển động cơ.
2. `controller_manager` không tự động tạo driver giao tiếp với động cơ.
3. Hardware Interface phải được triển khai và khai báo phù hợp với phần cứng thực tế.
4. Controller cần được load và activate trước khi sử dụng.
5. Tên Joint trong URDF phải tương thích với cấu hình controller.
6. `/joint_states` và `/tf` có vai trò khác nhau: một topic cung cấp trạng thái joint, topic còn lại cung cấp thông tin transform giữa các frame.
7. Có thể sử dụng package mô tả robot và cấu hình controller khác mà không cần thay đổi các package ROS 2 tiêu chuẩn, miễn là giao diện và cấu hình tương thích.