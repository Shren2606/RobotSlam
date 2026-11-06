# ROS 2 Package

## 1. Giới thiệu

Package này được phát triển trong hệ thống **RobotSlam**, sử dụng ROS 2 để triển khai các node xử lý dữ liệu, điều khiển robot và quản lý cấu hình hệ thống.

Package hỗ trợ kết hợp hai ngôn ngữ lập trình:
- **Python:** Triển khai các ROS 2 Node với file `.py`.
- **C++:** Triển khai các ROS 2 Node và thư viện xử lý với file `.cpp`, `.hpp`.
- **YAML:** Lưu trữ các tham số và cấu hình cho các node ROS 2.

## 2. Cấu trúc thư mục

```text
package_name/
│
├── package_name/          # Chứa các ROS 2 Node viết bằng Python
│   ├── node_1.py
│   ├── node_2.py
│   └── __init__.py
│
├── config/                # Chứa các file cấu hình YAML
│   ├── config_1.yaml
│   └── config_2.yaml
│
├── include/               # Chứa các file Header C++
│   └── package_name/
│       ├── header_1.hpp
│       └── header_2.hpp
│
├── src/                   # Chứa mã nguồn C++
│   ├── node_1.cpp
│   └── node_2.cpp
│
├── launch/                # Chứa các file Launch (nếu có)
│   └── package.launch.py
│
├── CMakeLists.txt         # Cấu hình biên dịch package
├── package.xml            # Khai báo thông tin và dependencies
└── README.md              # Tài liệu hướng dẫn package
```

## 3. Chức năng các thư mục

| Thư mục | Chức năng |
|---|---|
| `package_name/` | Chứa các node Python thực thi trong ROS 2. |
| `config/` | Chứa file YAML định nghĩa tham số và cấu hình node. |
| `include/` | Chứa các file Header `.hpp`, khai báo class, function và interface C++. |
| `src/` | Chứa mã nguồn `.cpp`, triển khai các class và function đã khai báo trong Header. |
| `launch/` | Chứa các file Launch để khởi chạy một hoặc nhiều node. |

## 4. Dependencies

Các thư viện phụ thuộc được khai báo trong `package.xml` và `CMakeLists.txt`.

Ví dụ:

- `rclpy`: ROS 2 Python Client Library.
- `rclcpp`: ROS 2 C++ Client Library.
- `std_msgs`: Các kiểu message cơ bản.
- `geometry_msgs`: Các message liên quan đến hình học và vận tốc.
- `sensor_msgs`: Các message dữ liệu cảm biến.

**Lưu ý:** Dependencies thực tế phụ thuộc vào chức năng của từng package.

## 5. Build Package

Di chuyển đến thư mục workspace:

```bash
cd ~/RobotSlam
```

Build package:

```bash
colcon build --packages-select package_name
```

Source môi trường ROS 2:

```bash
source install/setup.bash
```

## 6. Chạy Node

Chạy node Python:

```bash
ros2 run package_name node_1
```

Chạy node C++:

```bash
ros2 run package_name node_2
```

Chạy thông qua Launch file (nếu có):

```bash
ros2 launch package_name package.launch.py
```

## 7. Kiểm tra hoạt động

Kiểm tra các node đang chạy:

```bash
ros2 node list
```

Kiểm tra các topic:

```bash
ros2 topic list
```

Kiểm tra thông tin topic:

```bash
ros2 topic info /topic_name
```

---

**Project:** RobotSlam  
**Framework:** ROS 2 Jazzy  
**Build System:** Colcon / CMake / Python  
**Languages:** Python / C++  
