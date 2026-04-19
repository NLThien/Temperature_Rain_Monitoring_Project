// Code Arduino cho tp Đà Nẵng
#include <LiquidCrystal.h>
#include <DHT.h>

// Chân cảm biến DHT11
#define DHTPIN A0
#define DHTTYPE DHT11

// Chân cảm biến mưa
#define RAINPIN 8

// Chân LCD (RS, E, D4, D5, D6, D7)
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Hằng số khu vực
const String LOCATION = "DANANG";
// Biến lưu trạng thái hiện tại
float currentTemp = 35.0;   // nhiệt độ hiện tại (độ C)
float currentHum = 65.0;    // độ ẩm hiện tại (%)
int currentRain = 0;        // 0: không mưa, 1: có mưa

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
  pinMode(RAINPIN, INPUT_PULLUP);
  randomSeed(analogRead(A5));     // Khởi tạo bộ sinh số ngẫu nhiên
  // Khởi tạo giá trị ngẫu nhiên ban đầu trong khoảng thực tế
  currentTemp = random(180, 430) / 10.0;   // 18.0 - 43.0
  currentHum = random(400, 900) / 10.0;    // 40.0 - 90.0
  currentRain = random(0, 2);              // 0 hoặc 1
  lcd.print("Monitoring...");
  delay(2000);
}

// Hàm cập nhật nhiệt độ: thay đổi nhỏ ngẫu nhiên trong khoảng -0.5..0.5 độ
void updateTemperature() {
  float delta = (random(-50, 51)) / 100.0;  // -0.5 đến 0.5
  currentTemp += delta;
  // Giới hạn trong khoảng 15-40 độ C
  if (currentTemp < 15.0) currentTemp = 15.0;
  if (currentTemp > 40.0) currentTemp = 40.0;
}

// Hàm cập nhật độ ẩm: dựa trên nhiệt độ và trạng thái mưa
void updateHumidity() {
  // Độ ẩm cơ bản giảm khi nhiệt độ tăng (xu hướng ngược)
  float baseHum = 80.0 - (currentTemp - 20.0) * 1.5;
  if (baseHum < 30.0) baseHum = 30.0;
  if (baseHum > 95.0) baseHum = 95.0;
  
  // Nếu đang mưa, độ ẩm tăng lên 85-100%
  if (currentRain == 1) {
    baseHum = random(850, 1000) / 10.0;  // 85.0 - 100.0
  } else {
    // Thêm nhiễu ngẫu nhiên nhỏ ±3%
    float noise = (random(-30, 31)) / 10.0;
    baseHum += noise;
  }
  
  // Giới hạn độ ẩm 20-100%
  if (baseHum < 20.0) baseHum = 20.0;
  if (baseHum > 100.0) baseHum = 100.0;
  currentHum = baseHum;
}

// Hàm cập nhật trạng thái mưa: xác suất thay đổi nhỏ, và có thể duy trì trạng thái
void updateRain() {
  // Xác suất thay đổi trạng thái mưa: 5% mỗi lần loop
  if (random(100) < 5) {
    currentRain = 1 - currentRain;  // đảo trạng thái
  }
  // Nếu đang mưa, có thể tiếp tục mưa hoặc tạnh; không làm gì thêm
}

void loop() {
  // Cập nhật dữ liệu với mức độ thay đổi nhỏ
  updateTemperature();
  updateRain();       // cập nhật trạng thái mưa trước vì nó ảnh hưởng độ ẩm
  updateHumidity();   // độ ẩm phụ thuộc nhiệt độ và mưa

  // Gửi dữ liệu qua Serial (cho Python)
  Serial.print("LOCATION:");
  Serial.print(LOCATION);
  Serial.print("|NHIETDO:");
  Serial.print(currentTemp, 1);
  Serial.print("|DOAM:");
  Serial.print(currentHum, 0);
  Serial.print("|MUA:");
  Serial.println(currentRain);

  // Hiển thị lên LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(LOCATION);
  lcd.setCursor(0, 1);
  lcd.print("T:");
  lcd.print(currentTemp, 1);
  lcd.print("C H:");
  lcd.print(currentHum, 0);
  lcd.print("%");
  if (currentRain == 1) {
    lcd.setCursor(11, 0);
    lcd.print("RAIN");
  } else {
    lcd.print("Sunny Day");
  }

  delay(2000); // cập nhật dữ liệu mỗi 2s
}