#tự động đọc dữ liệu từ Proteus (qua cổng COM ảo) và gửi lên ThingsBoard
import serial
import requests
import json
import time

# Cấu hình Serial (kết nối với Proteus)
SERIAL_PORT = 'COM6'   # Cổng COM ảo đã tạo cho Python cổng 3
BAUD_RATE = 9600

# Cấu hình ThingsBoard
# Địa chỉ API và Access Token của thiết bị
THINGSBOARD_URL = "http://thingsboard.cloud/api/v1/KWjsJM5NAd3hEUlqQAYm/telemetry"
HEADERS = {"Content-Type": "application/json"}

print("Đang kết nối Serial...")
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Đã kết nối thành công tới {SERIAL_PORT}")
    time.sleep(2)  # Chờ ổn định
    ser.reset_input_buffer()
except Exception as e:
    print(f"Không thể mở cổng {SERIAL_PORT}: {e}")
    exit()

print("Bắt đầu đọc dữ liệu từ Proteus và gửi lên ThingsBoard...")
while True:
    if ser.in_waiting > 0:
        # 1. Đọc một dòng dữ liệu từ Proteus
        line = ser.readline().decode('utf-8').strip()
        print(f"Nhận từ Proteus: {line}")

        # 2. Phân tích dữ liệu (parse)
        # Ví dụ dữ liệu nhận được: "NHIETDO:26.50|DOAM:68.00|MUA:0"
        data_parts = line.split('|')
        telemetry = {}
        for part in data_parts:
            if ':' in part:
                key, value = part.split(':')
                if key == 'NHIETDO':
                    telemetry['temperature'] = float(value)
                elif key == 'DOAM':
                    telemetry['humidity'] = float(value)
                elif key == 'MUA':
                    telemetry['isRaining'] = int(value) == 1

        # 3. Gửi dữ liệu lên ThingsBoard bằng HTTP POST
        if telemetry:
            print(f"Đang gửi lên Cloud: {telemetry}")
            try:
                response = requests.post(THINGSBOARD_URL, headers=HEADERS, json=telemetry)
                if response.status_code == 200:
                    print("Gửi dữ liệu thành công!")
                else:
                    print(f"Gửi thất bại. Mã lỗi: {response.status_code}")
            except Exception as e:
                print(f"Lỗi kết nối đến ThingsBoard: {e}")

    time.sleep(0.5)