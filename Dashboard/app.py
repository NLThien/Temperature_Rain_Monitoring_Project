import serial
import threading
import time
import requests
import signal
import sys
from flask import Flask, jsonify, send_from_directory

# Khởi tạo ứng dụng Flask cho Web Dashboard
app = Flask(__name__, static_folder='.', static_url_path='')

# Dữ liệu lưu trữ tạm thời để hiển thị lên Web HTML
latest_weather_data = {
    "hanoi": {"temperature": 0.0, "humidity": 0.0, "isRaining": False},
    "danang": {"temperature": 0.0, "humidity": 0.0, "isRaining": False},
    "tphcm": {"temperature": 0.0, "humidity": 0.0, "isRaining": False}
}

# Cấu hình cho từng trạm của bạn
STATIONS = [
    {"name": "HANOI", "port": "COM8", "token": "WH57ZeLRwWVAHCeQpMMF"},
    {"name": "DANANG", "port": "COM4", "token": "95DgQAwzxY8NswbbKkM4"},
    {"name": "TPHCM", "port": "COM6", "token": "O1YqMX1BEPYG371fsVu5"},
]

THINGSBOARD_URL = "https://thingsboard.cloud/api/v1/{}/telemetry"
BAUD_RATE = 9600
stop_threads = False

# --- HÀM ĐỌC SERIAL VÀ GỬI LÊN THINGSBOARD (TỪ CODE CỦA BẠN) ---
def read_from_port(station_info):
    global stop_threads, latest_weather_data
    name = station_info["name"]
    port = station_info["port"]
    token = station_info["token"]
    
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        print(f"Đã kết nối {name} trên {port}")
        
        while not stop_threads:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"{name} nhận: {line}")
                    data_parts = line.split('|')
                    telemetry = {}
                    
                    for part in data_parts:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            if key == 'NHIETDO':
                                telemetry['temperature'] = float(value)
                                latest_weather_data[name.lower()]['temperature'] = float(value)
                            elif key == 'DOAM':
                                telemetry['humidity'] = float(value)
                                latest_weather_data[name.lower()]['humidity'] = float(value)
                            elif key == 'MUA':
                                telemetry['isRaining'] = int(value) == 1
                                latest_weather_data[name.lower()]['isRaining'] = int(value) == 1
                    
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

# --- API CHO WEB DASHBOARD (FLASK) ---
@app.route('/')
def index():
    # Trả về giao diện index.html
    return send_from_directory('.', 'index.html')

@app.route('/api/weather')
def get_weather():
    # File script.js sẽ gọi vào đây để lấy dữ liệu cập nhật lên giao diện
    return jsonify(latest_weather_data)

# --- XỬ LÝ DỪNG CHƯƠNG TRÌNH ---
def signal_handler(sig, frame):
    global stop_threads
    print("\nĐang dừng chương trình...")
    stop_threads = True
    time.sleep(1)
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    # 1. Bật các luồng (threads) đọc Serial của bạn lên trước
    threads = []
    for station in STATIONS:
        t = threading.Thread(target=read_from_port, args=(station,))
        t.daemon = True
        t.start()
        threads.append(t)
        time.sleep(1)
    
    # 2. Khởi động Web Server cho giao diện HTML/JS của bạn
    print("Giao diện Web đang chạy tại: http://localhost:5000")
    try:
        # Tắt debug để tránh việc Flask chạy 2 lần làm lỗi cổng COM
        app.run(host='0.0.0.0', port=5000, debug=False) 
    except KeyboardInterrupt:
        signal_handler(None, None)