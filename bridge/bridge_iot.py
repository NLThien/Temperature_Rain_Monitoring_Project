import serial
import paho.mqtt.client as mqtt
import json
import time

# ==========================================
# 1. CẤU HÌNH THINGSBOARD
# ==========================================
THINGSBOARD_HOST = 'eu.thingsboard.cloud'
ACCESS_TOKEN = '9mrOKVqmf0jvFtzOAOch' # Token thiết bị Tram_Thoi_Tiet của Thịnh

# ==========================================
# 2. CẤU HÌNH CỔNG SERIAL ẢO
# ==========================================
# Lưu ý: Nếu Proteus cắm vào COM1, thì ở đây phải là COM2
SERIAL_PORT = 'COM2' 
BAUD_RATE = 9600

# ==========================================
# 3. HÀM KẾT NỐI MQTT
# ==========================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Đã kết nối thành công với ThingsBoard Cloud!")
    else:
        print(f"❌ Lỗi kết nối, mã lỗi: {rc}")

# Thiết lập client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.username_pw_set(ACCESS_TOKEN)

# Bắt đầu kết nối
try:
    print("Đang kết nối tới ThingsBoard...")
    client.connect(THINGSBOARD_HOST, 1883, 60)
    client.loop_start() # Chạy nền tiến trình MQTT
except Exception as e:
    print(f"Lỗi mạng: {e}")
    exit()

# ==========================================
# 4. VÒNG LẶP ĐỌC DỮ LIỆU & GỬI LÊN CLOUD
# ==========================================
try:
    # Mở cổng Serial
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"🎧 Đang lắng nghe dữ liệu từ cổng {SERIAL_PORT}...\n")

    while True:
        if ser.in_waiting > 0:
            # Đọc 1 dòng dữ liệu từ Arduino gửi qua (ví dụ Arduino in ra: "28.5,70,0")
            raw_data = ser.readline().decode('utf-8').strip()
            print(f"📥 Arduino gửi: {raw_data}")

            try:
                # Tách chuỗi theo dấu phẩy
                data_list = raw_data.split(',')
                
                # Cấu trúc lại thành JSON cho ThingsBoard hiểu
                # Đảm bảo đúng thứ tự: Nhiệt độ, Độ ẩm, Mưa (Phụ thuộc vào code .ino của bạn)
                payload = {
                    "temperature": float(data_list[0]),
                    "humidity": float(data_list[1]),
                    "rain": int(data_list[2])
                }
                
                # Gửi lên Dashboard
                client.publish('v1/devices/me/telemetry', json.dumps(payload))
                print(f"🚀 Đã đẩy lên Dashboard: {payload}")
                print("-" * 40)
                
            except IndexError:
                print("⚠️ Lỗi: Arduino gửi thiếu dữ liệu. Cần đúng định dạng 'Nhiệt_độ,Độ_ẩm,Mưa'")
            except ValueError:
                print("⚠️ Lỗi: Không thể chuyển đổi dữ liệu thành số. Kiểm tra lại Arduino.")
                
        time.sleep(1) # Chờ 1 giây rồi đọc tiếp

except serial.SerialException:
    print(f"❌ Không thể mở cổng {SERIAL_PORT}. Hãy kiểm tra xem Virtual Serial Port đã bật chưa và cổng có bị phần mềm khác chiếm không.")
except KeyboardInterrupt:
    print("\n🛑 Đã dừng chương trình bằng tay.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
    client.loop_stop()
    client.disconnect()