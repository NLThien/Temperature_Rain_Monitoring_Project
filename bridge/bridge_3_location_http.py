# Đọc dữ liệu qua serial và đưa lên thingsboards

import serial
import threading
import time
import requests
import json
import signal
import sys

# Cấu hình cho từng trạm (Tên, Cổng COM, Token ThingsBoard)
STATIONS = [
    {"name": "HANOI", "port": "COM8", "token": "WH57ZeLRwWVAHCeQpMMF"},
    {"name": "DANANG", "port": "COM4", "token": "95DgQAwzxY8NswbbKkM4"},
    {"name": "TPHCM", "port": "COM6", "token": "O1YqMX1BEPYG371fsVu5"},
]

# URL gửi dữ liệu lên ThingsBoard
THINGSBOARD_URL = "https://thingsboard.cloud/api/v1/{}/telemetry"
BAUD_RATE = 9600

stop_threads = False # biến để dừng chương trình

def read_from_port(station_info):
    global stop_threads
    name = station_info["name"]
    port = station_info["port"]
    token = station_info["token"]
    
    try:
        # Mở cổng Serial
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        print(f"Đã kết nối {name} trên {port}")
        
        while not stop_threads:
            if ser.in_waiting:
                # Đọc một dòng dữ liệu
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"{name} nhận: {line}")
                    
                    # Phân tích dữ liệu
                    data_parts = line.split('|')
                    telemetry = {}
                    for part in data_parts:
                        if ':' in part:
                            key, value = part.split(':',1)
                            if key == 'NHIETDO':
                                telemetry['temperature'] = float(value)
                            elif key == 'DOAM':
                                telemetry['humidity'] = float(value)
                            elif key == 'MUA':
                                telemetry['isRaining'] = int(value) == 1
                    
                    # Gửi dữ liệu lên ThingsBoard
                    if telemetry:
                        url = THINGSBOARD_URL.format(token)
                        headers = {"Content-Type": "application/json"}
                        try:
                            response = requests.post(url, headers=headers, json=telemetry)
                            if response.status_code == 200:
                                print(f"{name} gửi lên Cloud thành công: {telemetry}")
                            else:
                                print(f"{name} gửi thất bại. Mã lỗi: {response.status_code}")
                        except Exception as e:
                            print(f"{name} lỗi kết nối ThingsBoard: {e}")
            time.sleep(0.5)
        ser.close()
        print(f"Đã đóng cổng {name} ({port})")
    except Exception as e:
        print(f"Lỗi mở cổng {port} cho {name}: {e}")

def signal_handler(sig, frame):
    global stop_threads
    print("\nĐang dừng chương trình...")
    stop_threads = True
    time.sleep(1)
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    threads = []
    for station in STATIONS:
        t = threading.Thread(target=read_from_port, args=(station,))
        t.daemon = True
        t.start()
        threads.append(t)
        time.sleep(1)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)