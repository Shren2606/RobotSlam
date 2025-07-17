#!/bin/bash

# === Kiểm tra quyền sudo trước ===
if [ "$EUID" -ne 0 ]; then
  echo "⚠️ Vui lòng chạy script với sudo:"
  echo "    sudo $0"
  exit 1
fi

# === Lấy địa chỉ MAC của adapter Bluetooth ===
echo "📡 Đang lấy địa chỉ MAC Bluetooth..."
adapter_mac=$(hciconfig | grep -oP '(?<=BD Address: )([0-9A-F:]{17})' | head -n 1)

if [ -z "$adapter_mac" ]; then
  echo "❌ Không tìm thấy thiết bị Bluetooth. Hãy bật Bluetooth hoặc cắm USB dongle."
  exit 1
fi

echo "✅ Địa chỉ Bluetooth của máy: $adapter_mac"

# === Gán địa chỉ MAC vào tay cầm PS3 ===
echo "🔌 Cắm tay cầm PS3 qua cáp USB và ấn Enter..."
read

echo "🔧 Đang gán địa chỉ Bluetooth cho tay cầm..."
sixpair

# === Restart dịch vụ bluetooth ===
echo "🔁 Khởi động lại dịch vụ Bluetooth..."
systemctl restart bluetooth
sleep 2

# === Bluetoothctl: dò và kết nối ===
echo "📡 Dò tìm tay cầm Bluetooth PS3..."
bluetoothctl <<EOF
power on
agent on
default-agent
scan on
EOF

echo ""
echo "⏳ Đợi khoảng 5–10 giây để thấy tay cầm hiển thị..."
echo "📋 Các thiết bị đang hiện ra sẽ được hiển thị liên tục (trong log)."
echo "👉 Khi thấy tay cầm xuất hiện (thường tên là PLAYSTATION), hãy nhập địa chỉ MAC của tay cầm bên dưới."
echo "🔍 Đang tìm MAC tay cầm PS3 trong danh sách thiết bị..."
ps3_mac=$(bluetoothctl devices | grep -i "playstation\|panhai" | awk '{print $2}' | head -n 1)

if [ -z "$ps3_mac" ]; then
  echo "❌ Không tìm thấy tay cầm PS3 tự động. Vui lòng chạy lại script và nhập tay."
  exit 1
fi

echo "✅ Tìm thấy tay cầm PS3: $ps3_mac"


# === Tin cậy và kết nối tay cầm ===
bluetoothctl <<EOF
scan off
trust $ps3_mac
pair $ps3_mac
connect $ps3_mac
EOF

echo ""
echo "✅ Kết nối hoàn tất! Kiểm tra bằng lệnh:"
echo "    jstest /dev/input/js0"


