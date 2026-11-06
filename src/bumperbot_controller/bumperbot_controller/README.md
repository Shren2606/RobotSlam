# Python Nodes – Differential Drive Controller

## 1. Giới thiệu

Thư mục này chứa hai ROS 2 Node được viết bằng Python, phục vụ việc điều khiển và ước lượng chuyển động cho robot sử dụng cơ cấu truyền động vi sai (**Differential Drive**).

Hai node được triển khai:

| Node | Chức năng |
|---|---|
| `simple_controller` | Chuyển đổi vận tốc robot thành vận tốc góc bánh xe và tính toán Odometry từ dữ liệu Encoder. |
| `noisy_controller` | Tính toán Odometry từ dữ liệu Encoder có bổ sung nhiễu Gaussian để mô phỏng sai số cảm biến. |

Cả hai node sử dụng dữ liệu vị trí khớp bánh xe (`JointState`) để tính toán vận tốc, vị trí và hướng di chuyển của robot.

Kết quả được xuất dưới dạng:
- Odometry (`nav_msgs/Odometry`).
- Coordinate Transform (`TF2`).

---

## 2. Cấu trúc thư mục

```text
package_name/
└── package_name/
    ├── __init__.py
    ├── simple_controller.py
    ├── noisy_controller.py
    └── README.md
```

---

## 3. Simple Controller Node

### 3.1. Giới thiệu

`simple_controller.py` triển khai node `simple_controller`, thực hiện hai nhiệm vụ chính:

1. Nhận vận tốc điều khiển từ hệ thống ROS 2 và chuyển đổi thành vận tốc góc của hai bánh xe.
2. Nhận dữ liệu Encoder từ `joint_states`, tính toán vận tốc và vị trí robot, sau đó xuất bản Odometry và TF.

Node sử dụng mô hình động học vi sai để thực hiện chuyển đổi giữa vận tốc robot và vận tốc bánh xe.

### 3.2. Parameters

| Parameter | Type | Default | Đơn vị | Mô tả |
|---|---|---:|---|---|
| `wheel_radius` | double | 0.033 | m | Bán kính bánh xe. |
| `wheel_separation` | double | 0.17 | m | Khoảng cách giữa hai bánh xe. |

Các tham số được khai báo và đọc khi khởi tạo node.

### 3.3. Subscribers

| Topic | Message Type | Mô tả |
|---|---|---|
| `/bumperbot_controller/cmd_vel` | `geometry_msgs/TwistStamped` | Nhận vận tốc tuyến tính và vận tốc góc của robot. |
| `/joint_states` | `sensor_msgs/JointState` | Nhận vị trí góc của hai bánh xe từ Encoder hoặc hệ thống mô phỏng. |

### 3.4. Publishers

| Topic | Message Type | Mô tả |
|---|---|---|
| `/simple_velocity_controller/commands` | `std_msgs/Float64MultiArray` | Xuất bản vận tốc góc của hai bánh xe. |
| `/bumperbot_controller/odom` | `nav_msgs/Odometry` | Xuất bản thông tin vị trí, hướng và vận tốc của robot. |

**Thứ tự vận tốc bánh xe:**

```text
commands[0] = Right Wheel Velocity
commands[1] = Left Wheel Velocity
```

### 3.5. Differential Drive Inverse Kinematics

Node sử dụng mô hình động học nghịch để chuyển đổi vận tốc robot thành vận tốc góc của hai bánh xe.

**Định nghĩa:**

- $v$: Vận tốc tuyến tính của robot (m/s).
- $\omega$: Vận tốc góc của robot (rad/s).
- $r$: Bán kính bánh xe (m).
- $L$: Khoảng cách giữa hai bánh xe (m).
- $\omega_R$: Vận tốc góc bánh phải (rad/s).
- $\omega_L$: Vận tốc góc bánh trái (rad/s).

**Công thức:**

$$
\omega_R = \frac{v+\frac{L}{2}\omega}{r}
$$

$$
\omega_L = \frac{v-\frac{L}{2}\omega}{r}
$$

Node sử dụng ma trận chuyển đổi và phép nghịch đảo ma trận bằng NumPy để tính toán vận tốc bánh xe.

### 3.6. Odometry Calculation

Node sử dụng sự thay đổi vị trí góc của hai bánh xe để ước lượng chuyển động robot.

**Bước 1: Tính độ dịch chuyển góc bánh xe**

$$
\Delta\phi_L = \phi_L(k)-\phi_L(k-1)
$$

$$
\Delta\phi_R = \phi_R(k)-\phi_R(k-1)
$$

**Bước 2: Tính vận tốc góc bánh xe**

$$
\dot{\phi}_L = \frac{\Delta\phi_L}{\Delta t}
$$

$$
\dot{\phi}_R = \frac{\Delta\phi_R}{\Delta t}
$$

**Bước 3: Tính vận tốc robot**

$$
v = \frac{r(\dot{\phi}_R+\dot{\phi}_L)}{2}
$$

$$
\omega = \frac{r(\dot{\phi}_R-\dot{\phi}_L)}{L}
$$

**Bước 4: Tính độ dịch chuyển robot**

$$
\Delta s = \frac{r(\Delta\phi_R+\Delta\phi_L)}{2}
$$

$$
\Delta\theta = \frac{r(\Delta\phi_R-\Delta\phi_L)}{L}
$$

**Bước 5: Cập nhật vị trí robot**

$$
\theta_k = \theta_{k-1}+\Delta\theta
$$

$$
x_k = x_{k-1}+\Delta s\cos(\theta_k)
$$

$$
y_k = y_{k-1}+\Delta s\sin(\theta_k)
$$

### 3.7. TF Broadcasting

Node sử dụng `TransformBroadcaster` để xuất bản phép biến đổi tọa độ:

```text
odom
 └── base_footprint
```

Trong đó:

- `odom`: Hệ tọa độ tham chiếu cố định tương đối với chuyển động ước lượng.
- `base_footprint`: Hệ tọa độ gắn với robot trên mặt phẳng di chuyển.

Góc quay của robot được chuyển từ Euler yaw sang Quaternion bằng `tf_transformations`.

---

## 4. Noisy Controller Node

### 4.1. Giới thiệu

`noisy_controller.py` triển khai node `noisy_controller`, có chức năng tính toán Odometry tương tự `simple_controller`.

Điểm khác biệt là node bổ sung nhiễu Gaussian vào dữ liệu vị trí Encoder trước khi thực hiện tính toán.

Mục đích:
- Mô phỏng sai số trong quá trình đọc Encoder.
- Đánh giá ảnh hưởng của nhiễu cảm biến đến Odometry.
- Tạo nguồn dữ liệu Odometry không hoàn hảo phục vụ thử nghiệm các thuật toán lọc và hợp nhất dữ liệu cảm biến, chẳng hạn như EKF.

### 4.2. Parameters

| Parameter | Type | Default | Đơn vị | Mô tả |
|---|---|---:|---|---|
| `wheel_radius` | double | 0.033 | m | Bán kính bánh xe. |
| `wheel_separation` | double | 0.17 | m | Khoảng cách giữa hai bánh xe. |

### 4.3. Subscribers

| Topic | Message Type | Mô tả |
|---|---|---|
| `/joint_states` | `sensor_msgs/JointState` | Nhận vị trí góc của hai bánh xe. |

### 4.4. Publishers

| Topic | Message Type | Mô tả |
|---|---|---|
| `/bumperbot_controller/odom_noisy` | `nav_msgs/Odometry` | Xuất bản Odometry có nhiễu. |

### 4.5. Gaussian Noise Model

Node sử dụng thư viện NumPy để tạo nhiễu Gaussian:

```python
wheel_encoder_left = msg.position[1] + np.random.normal(0, 0.005)

wheel_encoder_right = msg.position[0] + np.random.normal(0, 0.005)
```

Mô hình nhiễu:

$$
\epsilon \sim \mathcal{N}(\mu,\sigma^2)
$$

Trong đó:

| Thông số | Giá trị | Ý nghĩa |
|---|---:|---|
| Mean (\(\mu\)) | 0 | Giá trị trung bình của nhiễu. |
| Standard deviation (\(\sigma\)) | 0.005 | Độ lệch chuẩn của nhiễu. |
| Variance (\(\sigma^2\)) | 0.000025 | Phương sai của nhiễu. |

Giá trị nhiễu được cộng trực tiếp vào vị trí góc Encoder trước khi tính toán Odometry.

**Lưu ý:** Nhiễu được tạo độc lập cho mỗi bánh xe và mỗi lần nhận dữ liệu `joint_states`.

### 4.6. Odometry Calculation

Sau khi bổ sung nhiễu, node thực hiện các bước tính toán:

1. Tính độ dịch chuyển góc của hai bánh xe.
2. Tính vận tốc góc của từng bánh xe.
3. Tính vận tốc tuyến tính và vận tốc góc của robot.
4. Tính độ dịch chuyển và hướng di chuyển.
5. Cập nhật vị trí robot trong hệ tọa độ `odom`.
6. Xuất bản Odometry và TF.

Các công thức động học được sử dụng giống với `simple_controller`.

### 4.7. TF Broadcasting

Node xuất bản phép biến đổi tọa độ:

```text
odom
 └── base_footprint_noisy
```

Frame `base_footprint_noisy` được sử dụng để phân biệt kết quả ước lượng có nhiễu với frame của robot chính.

---

## 5. So sánh hai Node

| Đặc điểm | Simple Controller | Noisy Controller |
|---|---|---|
| Nhận `cmd_vel` | Có | Không |
| Nhận `joint_states` | Có | Có |
| Bổ sung nhiễu Encoder | Không | Có |
| Tính toán Odometry | Có | Có |
| Xuất bản TF | Có | Có |
| Odometry Topic | `bumperbot_controller/odom` | `bumperbot_controller/odom_noisy` |
| Child Frame | `base_footprint` | `base_footprint_noisy` |

---

## 6. Dependencies

Các thư viện cần thiết:

| Package / Library | Chức năng |
|---|---|
| `rclpy` | ROS 2 Python Client Library. |
| `std_msgs` | Các kiểu message cơ bản. |
| `geometry_msgs` | Các message vận tốc và Transform. |
| `sensor_msgs` | Message JointState. |
| `nav_msgs` | Message Odometry. |
| `tf2_ros` | Phát sóng TF. |
| `tf_transformations` | Chuyển đổi Euler sang Quaternion. |
| `python3-numpy` | Tính toán ma trận và tạo nhiễu Gaussian. |

---

## 7. Cách chạy Node

### 7.1. Build Package

```bash
cd ~/RobotSlam

colcon build --packages-select package_name

source install/setup.bash
```

### 7.2. Chạy Simple Controller

```bash
ros2 run package_name simple_controller
```

Có thể truyền tham số trực tiếp:

```bash
ros2 run package_name simple_controller --ros-args \
-p wheel_radius:=0.033 \
-p wheel_separation:=0.17
```

### 7.3. Chạy Noisy Controller

```bash
ros2 run package_name noisy_controller
```

Truyền tham số:

```bash
ros2 run package_name noisy_controller --ros-args \
-p wheel_radius:=0.033 \
-p wheel_separation:=0.17
```

---

## 8. Kiểm tra hoạt động

Kiểm tra các node:

```bash
ros2 node list
```

Kiểm tra các topic:

```bash
ros2 topic list
```

Kiểm tra Odometry:

```bash
ros2 topic echo /bumperbot_controller/odom
```

Kiểm tra Odometry có nhiễu:

```bash
ros2 topic echo /bumperbot_controller/odom_noisy
```

Kiểm tra TF:

```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

```bash
ros2 run tf2_ros tf2_echo odom base_footprint_noisy
```

---

## 9. Lưu ý kỹ thuật

1. Thứ tự bánh xe trong `JointState.position` phải đúng với thứ tự mà node đang sử dụng: vị trí `[0]` là bánh phải và `[1]` là bánh trái.
2. Các tham số bán kính bánh xe và khoảng cách hai bánh phải phù hợp với kích thước thực tế hoặc mô hình robot.
3. `joint_states` phải cung cấp timestamp hợp lệ để tính toán khoảng thời gian giữa hai lần cập nhật.
4. Node `noisy_controller` chỉ mô phỏng nhiễu trên dữ liệu vị trí Encoder, không phải mô hình nhiễu vật lý đầy đủ của cảm biến.
5. Hai node đang sử dụng chung dữ liệu `joint_states`, nhưng xuất bản Odometry và TF trên các frame khác nhau.
6. Khi sử dụng đồng thời hai node, cần bảo đảm không có node khác xuất bản trùng các phép biến đổi TF.

**Lưu ý về triển khai:** Trong phiên bản hiện tại, `noisy_controller` cập nhật vị trí Encoder trước bằng dữ liệu đã cộng nhiễu, nhưng lưu vị trí Encoder trước đó bằng dữ liệu gốc. Vì vậy, nhiễu có thể ảnh hưởng đến cả độ dịch chuyển ở những chu kỳ tiếp theo. Đây là điểm cần cân nhắc nếu muốn xây dựng mô hình nhiễu Encoder chính xác hơn.

Ngoài ra, cần xử lý trường hợp `dt <= 0` trước khi chia để tránh lỗi tính toán vận tốc.