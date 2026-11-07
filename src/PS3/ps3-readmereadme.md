# KẾT NỐI TAY CẦM PS3 QUA BLUETOOTH

## 1. Giới thiệu

Tài liệu hướng dẫn cấu hình và kết nối tay cầm PS3 (DualShock 3) với máy tính Ubuntu thông qua Bluetooth.

Mục đích:
- Kết nối tay cầm PS3 với máy tính bằng Bluetooth.
- Gán địa chỉ Bluetooth của máy tính vào tay cầm PS3.
- Thiết lập ghép đôi và kết nối tay cầm.
- Kiểm tra tín hiệu điều khiển thông qua thiết bị `/dev/input/js0`.

## 2. Cài đặt các gói cần thiết

Cập nhật danh sách package:

```bash
sudo apt update
```

Cài đặt các công cụ Bluetooth và joystick:

```bash
sudo apt install bluetooth bluez joystick -y
```

Cài đặt thêm `sixpair` nếu hệ thống chưa có. `sixpair` là công cụ dùng để gán địa chỉ Bluetooth của máy tính vào tay cầm PS3.

Kiểm tra:

```bash
which sixpair
```

Nếu không tìm thấy, cần cài đặt hoặc biên dịch công cụ `sixpair` trước khi chạy script.

## 3. Cấu hình Bluetooth

Mở file cấu hình:

```bash
sudo nano /etc/bluetooth/input.conf
```

Tìm dòng:

```ini
#ClassicBondedOnly=true
```

Chỉnh thành:

```ini
ClassicBondedOnly=false
```

Lưu file:
- `Ctrl + O`: Lưu.
- `Enter`: Xác nhận.
- `Ctrl + X`: Thoát.

Khởi động lại dịch vụ Bluetooth:

```bash
sudo systemctl restart bluetooth
```

## 4. Chuẩn bị script kết nối

Tạo file:

```bash
nano name_file_sh.sh
```

Dán nội dung script kết nối PS3 vào file, sau đó lưu lại.

Cấp quyền thực thi:

```bash
chmod +x name_file_sh.sh
```

## 5. Quy trình kết nối tay cầm PS3

**Lưu ý:** Bật Bluetooth trên máy tính và cắm Bluetooth USB dongle (nếu sử dụng) trước khi chạy script.

Thực hiện theo thứ tự:

**Bước 1: Chạy script**

```bash
sudo ./name_file_sh.sh
```

**Bước 2: Kết nối tay cầm bằng cáp USB**

Khi script hiển thị:

```text
Cắm tay cầm PS3 qua cáp USB và ấn Enter...
```

Cắm tay cầm PS3 vào máy tính bằng cáp USB có hỗ trợ truyền dữ liệu, sau đó nhấn `Enter`.

Script sẽ sử dụng `sixpair` để gán địa chỉ Bluetooth của máy tính vào tay cầm.

**Bước 3: Dò tìm thiết bị Bluetooth**

Script khởi động lại dịch vụ Bluetooth và bật chế độ dò tìm thiết bị.

Tay cầm PS3 có thể xuất hiện với tên như `PLAYSTATION`.

**Bước 4: Ghép đôi và kết nối**

Script tự động tìm địa chỉ MAC của tay cầm, sau đó thực hiện:

```bash
trust <MAC_ADDRESS>
pair <MAC_ADDRESS>
connect <MAC_ADDRESS>
```

Nếu không tìm thấy thiết bị tự động, cần kiểm tra danh sách thiết bị bằng:

```bash
bluetoothctl devices
```

Sau đó lấy địa chỉ MAC của tay cầm để ghép đôi thủ công.

## 6. Kiểm tra kết nối

Sau khi kết nối thành công, kiểm tra thiết bị joystick:

```bash
ls /dev/input/js*
```

Nếu xuất hiện:

```text
/dev/input/js0
```

Kiểm tra tín hiệu từ tay cầm:

```bash
jstest /dev/input/js0
```

Nhấn các nút và di chuyển cần analog để kiểm tra giá trị thay đổi.

Có thể kiểm tra thông tin thiết bị bằng:

```bash
ls -l /dev/input/js0
```

## 7. Xử lý lỗi thường gặp

### 7.1. Không tìm thấy Bluetooth adapter

Kiểm tra:

```bash
hciconfig
```

Hoặc:

```bash
bluetoothctl list
```

Nếu không thấy adapter, kiểm tra Bluetooth đã được bật hay chưa và USB dongle đã được hệ thống nhận diện chưa.

### 7.2. Không tìm thấy lệnh sixpair

Kiểm tra:

```bash
which sixpair
```

Nếu không có kết quả, cần cài đặt hoặc biên dịch `sixpair`.

### 7.3. Không tìm thấy tay cầm PS3

Kiểm tra danh sách thiết bị:

```bash
bluetoothctl devices
```

Đảm bảo tay cầm đã được kết nối USB và đã chạy `sixpair` thành công.

Có thể bật dò tìm thủ công:

```bash
bluetoothctl
```

Sau đó nhập:

```text
power on
agent on
default-agent
scan on
```

### 7.4. Không xuất hiện /dev/input/js0

Kiểm tra thiết bị input:

```bash
ls /dev/input/
```

Kiểm tra module joystick:

```bash
sudo modprobe joydev
```

Sau đó rút và kết nối lại tay cầm.

## 8. Lưu ý khi sử dụng ROS 2

Sau khi kết nối tay cầm thành công, có thể sử dụng `joy` package của ROS 2 để đọc dữ liệu điều khiển.

Cài đặt:

```bash
sudo apt install ros-jazzy-joy -y
```

Chạy node đọc tay cầm:

```bash
ros2 run joy joy_node
```

Kiểm tra dữ liệu:

```bash
ros2 topic echo /joy
```

Nếu nhận được dữ liệu `axes` và `buttons` khi thao tác trên tay cầm, thiết bị đã có thể sử dụng để điều khiển robot thông qua ROS 2.

## 9. Ghi chú về WSL2

Nếu sử dụng Ubuntu trên WSL2:

- Bluetooth adapter của Windows không tự động xuất hiện trong WSL2.
- Cần chuyển tiếp thiết bị USB Bluetooth vào WSL2 nếu muốn sử dụng USB dongle.
- Kiểm tra thiết bị bằng `lsusb` sau khi chuyển tiếp.
- Khả năng hoạt động của Bluetooth và `systemctl` phụ thuộc cấu hình WSL2, đặc biệt là systemd.

**Lưu ý:** Script cần được kiểm tra trên Ubuntu chạy trực tiếp trước khi sử dụng trong WSL2. Một số lệnh như `hciconfig` có thể không còn được cài mặc định trên các bản Ubuntu mới.