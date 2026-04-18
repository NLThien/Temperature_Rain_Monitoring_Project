#include <LiquidCrystal.h>
#include <DHT.h>

// Chân cảm biến DHT11
#define DHTPIN A0
#define DHTTYPE DHT11

// Chân cảm biến mưa (đổi sang chân 8 để tránh xung đột với LCD)
#define RAINPIN 8

// Chân LCD (RS, E, D4, D5, D6, D7)
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  lcd.begin(16, 2);
  pinMode(RAINPIN, INPUT_PULLUP);  // Dùng điện trở kéo lên nội bộ
  lcd.print("Monitoring...");
  delay(2000);
}

void loop() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int rainState = digitalRead(RAINPIN);  // LOW = có mưa (vì nút nhấn nối GND)

  // Gửi dữ liệu qua Serial (cho Python)
  Serial.print("NHIETDO:");
  Serial.print(t);
  Serial.print("|DOAM:");
  Serial.print(h);
  Serial.print("|MUA:");
  Serial.println(rainState == LOW ? 1 : 0);

  // Hiển thị lên LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(t);
  lcd.print(" C H:");
  lcd.print(h);
  lcd.print("%");
  lcd.setCursor(0, 1);
  if (rainState == LOW) {
    lcd.print("** RAINING **");
  } else {
    lcd.print("Sunny Day    ");
  }

  delay(2000);
}