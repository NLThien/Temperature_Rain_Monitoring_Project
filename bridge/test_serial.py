import serial
import time

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Mở cổng {SERIAL_PORT} thành công")
except Exception as e:
    print(f"Lỗi mở cổng: {e}")
    exit()

print("Đang chờ dữ liệu... ")
try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            if data:
                print(f"Nhận: {data}")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nKết thúc")
    ser.close()