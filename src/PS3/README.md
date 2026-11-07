# CẤU HÌNH UDEV RULES TRÊN UBUNTU

## 1. Giới thiệu

Udev Rules là các quy tắc dùng để quản lý và phân quyền truy cập thiết bị phần cứng trên Ubuntu.

Cấu hình này hỗ trợ các thiết bị:

- Tay cầm điều khiển PS3 (Game Controller).
- Arduino Mega, Arduino Uno.
- ESP32 / ESP8266.
- Bộ chuyển đổi USB sang UART (CP210x, CH340).

### Mục đích

- Cho phép chương trình truy cập thiết bị mà không cần sử dụng `sudo`.
- Tự động phân quyền khi kết nối thiết bị USB.
- Hỗ trợ giao tiếp giữa ROS 2 và các thiết bị phần cứng.
- Hạn chế phải cấp quyền thủ công mỗi lần kết nối USB.

---

## 2. Cấu hình thiết bị Input (Tay cầm điều khiển)

### 2.1. Tạo file cấu hình

```bash
sudo nano /etc/udev/rules.d/81-event.rules
```

### 2.2. Nội dung cấu hình

```udev
# Phân quyền truy cập cho các thiết bị input event
SUBSYSTEM=="input", KERNEL=="event*", GROUP="input", MODE="0660"
```

### 2.3. Giải thích

| Tham số | Ý nghĩa |
|---|---|
| `SUBSYSTEM=="input"` | Áp dụng cho các thiết bị đầu vào |
| `KERNEL=="event*"` | Áp dụng cho các thiết bị `/dev/input/event*` |
| `GROUP="input"` | Gán nhóm quản lý thiết bị là input |
| `MODE="0660"` | Cấp quyền đọc và ghi cho owner và group |

**Mục đích:** Cho phép các chương trình như ROS 2 `joy_node` truy cập tay cầm điều khiển mà không cần quyền root.

---

## 3. Cấu hình Arduino

### 3.1. Tạo file cấu hình

```bash
sudo nano /etc/udev/rules.d/99-arduino.rules
```

### 3.2. Nội dung cấu hình

```udev
# Phân quyền truy cập cho thiết bị Arduino
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", MODE="0666", GROUP="dialout"
```

### 3.3. Giải thích

| Tham số | Ý nghĩa |
|---|---|
| `SUBSYSTEM=="tty"` | Áp dụng cho thiết bị cổng Serial |
| `ATTRS{idVendor}=="2341"` | Nhận diện Vendor ID của Arduino |
| `MODE="0666"` | Cấp quyền đọc và ghi cho mọi người dùng |
| `GROUP="dialout"` | Gán nhóm quản lý cổng Serial |

**Mục đích:** Cho phép ROS 2 và các chương trình giao tiếp Serial truy cập Arduino thông qua các cổng như `/dev/ttyACM0`.

**Lưu ý:** Vendor ID `2341` thường được sử dụng bởi các board Arduino chính hãng. Những board tương thích có thể sử dụng Vendor ID khác.

---

## 4. Cấu hình ESP32 / ESP8266

Các board ESP32 / ESP8266 thường sử dụng IC chuyển đổi USB sang UART để giao tiếp với máy tính.

Hai loại IC phổ biến là CP210x và CH340.

### 4.1. Tạo file cấu hình

```bash
sudo nano /etc/udev/rules.d/99-esp8266.rules
```

### 4.2. Nội dung cấu hình

**Trường hợp sử dụng CP210x:**

```udev
# Phân quyền cho IC chuyển đổi USB-UART CP210x
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
```

**Trường hợp sử dụng CH340:**

```udev
# Phân quyền cho IC chuyển đổi USB-UART CH340
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="dialout"
```

### 4.3. Thông tin Vendor ID và Product ID

| IC USB-UART | Vendor ID | Product ID |
|---|---|---|
| CP210x | `10c4` | `ea60` |
| CH340 | `1a86` | `7523` |

**Mục đích:** Cho phép truy cập các cổng Serial của ESP32 / ESP8266 mà không cần sử dụng `sudo`.

Các cổng thiết bị thường gặp:

- `/dev/ttyUSB0`
- `/dev/ttyUSB1`

**Lưu ý:** Chỉ cần sử dụng quy tắc tương ứng với IC USB-UART trên board của bạn. Nếu sử dụng IC khác, cần xác định lại Vendor ID và Product ID.

---

## 5. Xác định Vendor ID và Product ID

Để xác định thông tin USB của thiết bị, kết nối thiết bị với máy tính và chạy:

```bash
lsusb
```

Ví dụ kết quả:

```text
Bus 001 Device 005: ID 10c4:ea60 Silicon Labs CP210x UART Bridge
```

Trong đó:

- Vendor ID: `10c4`
- Product ID: `ea60`

Sử dụng hai thông số này để khai báo trong file udev rules.

Cú pháp:

```udev
ATTRS{idVendor}=="VENDOR_ID"
ATTRS{idProduct}=="PRODUCT_ID"
```

---

## 6. Nạp lại cấu hình Udev Rules

Sau khi tạo hoặc chỉnh sửa các file cấu hình, chạy:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Sau đó ngắt kết nối và kết nối lại thiết bị USB để áp dụng cấu hình mới.

---

## 7. Phân quyền cho người dùng

Thêm tài khoản hiện tại vào các nhóm quản lý thiết bị:

```bash
sudo usermod -aG dialout,input $USER
```

Ý nghĩa:

- `dialout`: Cho phép truy cập các thiết bị Serial.
- `input`: Cho phép truy cập các thiết bị đầu vào như tay cầm điều khiển.

Sau khi thực hiện, cần đăng xuất và đăng nhập lại để cập nhật quyền.

Kiểm tra các nhóm hiện tại:

```bash
groups
```

Kết quả mong muốn có:

```text
dialout input
```

---

## 8. Kiểm tra quyền truy cập thiết bị

### 8.1. Kiểm tra Arduino

```bash
ls -l /dev/ttyACM*
```

### 8.2. Kiểm tra ESP32 / ESP8266

```bash
ls -l /dev/ttyUSB*
```

### 8.3. Kiểm tra tay cầm điều khiển

```bash
ls -l /dev/input/event*
```

### 8.4. Kiểm tra thông tin Udev

Ví dụ:

```bash
udevadm info --query=all --name=/dev/ttyUSB0
```

Thay `/dev/ttyUSB0` bằng đường dẫn thiết bị thực tế.

---

## 9. Lưu ý khi sử dụng WSL2

Đối với Ubuntu 24.04 chạy trên WSL2:

1. Cài đặt `usbipd-win` trên Windows.
2. Kết nối và chuyển thiết bị USB từ Windows sang WSL2.
3. Kiểm tra thiết bị đã được nhận diện trong Ubuntu bằng lệnh `lsusb`.
4. Kiểm tra dịch vụ udev có hoạt động hay không.
5. Nạp lại udev rules sau khi cấu hình.

**Lưu ý:** Udev Rules chỉ quản lý quyền truy cập thiết bị trong Ubuntu, không có chức năng chuyển tiếp thiết bị USB từ Windows sang WSL2. Cần cấu hình USB passthrough riêng.

---

## 10. Tổng kết

| File cấu hình | Thiết bị | Chức năng |
|---|---|---|
| `81-event.rules` | Tay cầm điều khiển | Phân quyền thiết bị Input |
| `99-arduino.rules` | Arduino | Phân quyền cổng Serial |
| `99-esp8266.rules` | ESP32 / ESP8266 | Phân quyền USB-UART |

Sau khi hoàn thành, Ubuntu có thể tự động áp dụng quyền truy cập cho các thiết bị phần cứng tương ứng khi được kết nối.

Cấu hình này hỗ trợ quá trình phát triển ROS 2, lập trình nhúng và giao tiếp giữa máy tính với robot.