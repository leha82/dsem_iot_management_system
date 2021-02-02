//1602 LCD 세팅
#include <LiquidCrystal.h>               // LCD 라이브러리 포함
LiquidCrystal lcd(13, 12, 5, 4, 3, 2);   // LCD 핀 설정

#include <SoftwareSerial.h>
SoftwareSerial BTSerial(8,9); // Tx, Rx

// DHT11 Settings...
#include "DHT.h"           
#define DHTPIN 7                
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

//먼지센서 세팅
int DUST_LED = 11;
int DUST = 0;
int samplingTime = 280;
int deltaTime = 40;
int sleepTime = 9680;
float dustval = 0;
float voltage = 0;
float dustug = 0;
float dus = 0;
float a = 0;

// LED light setting
int LED_LIGHT = 10;
int LED_STATUS = 0;

// cds Settings...
int cds = 0;

// Device Number
String arduino_num = "04";

void setup() {
  Serial.begin(9600);        // 시리얼 통신 시작
  lcd.begin(16, 2);           // 16x2 LCD 선언
  pinMode(DUST_LED, OUTPUT);  // 먼지센서 LED 핀 설정
  BTSerial.begin(9600); // 블루투스 시리얼 개방

  pinMode(LED_LIGHT, OUTPUT);
}

void loop() {
  // DustSensor code
  digitalWrite(DUST_LED, LOW); // 적외선 LED ON
  delayMicroseconds(samplingTime);
  dustval = analogRead(DUST); //먼지센서 값 읽기
  delayMicroseconds(deltaTime);
  digitalWrite(DUST_LED, HIGH); // 적외선 LED OFF
  delayMicroseconds(sleepTime);
  voltage = dustval * (5.0 / 1024.0);  // 전압 구하기, 전압 단위 : V
  dustug = 0.17 * voltage;      // ug 단위 변환
  dus = dustug * 1000;

  // dht11 code
  int h = dht.readHumidity(); 
  int t = dht.readTemperature();

  // cds code
  cds = analogRead(A2);

  // Serial Monitor
  Serial.print(arduino_num);
  Serial.print(":");
  Serial.print(h); Serial.print(" ");
  Serial.print(t); Serial.print(" ");
  Serial.print(cds); Serial.print(" ");
  Serial.print(dus); Serial.print(" ");
  Serial.print(LED_STATUS); Serial.print("!");
  Serial.println();

  //1602 LCD 모듈 코드
  lcd.clear();
  analogWrite(6, 120);
  lcd.setCursor(0, 0);
  lcd.print("H: ");
  lcd.print(h);
  lcd.print(" %  ");
  lcd.print("T: ");
  lcd.print(t);
  lcd.print(" C");
  lcd.setCursor(0, 1);
  lcd.print("Dust: ");
  if (dus > 0) {
    a = dus;
    lcd.print(a);
  }
  else {
    lcd.print(a);
  }
  lcd.print("ug");

  // LED Light Change
  digitalWrite(LED_LIGHT, LED_STATUS);
//  if (a < 35) {   // 좋음
//    digitalWrite(10, HIGH);
//  }
//  if (a > 35 & a < 75) {  // 나쁨
//    digitalWrite(10, LOW); delay(1000);
//    digitalWrite(10, HIGH);
//  }
//  if (a > 75) {       // 매우 나쁨
//    digitalWrite(10, LOW); delay(500);
//    digitalWrite(10, HIGH);  
//  }
    
  // BluetoothSerial print
  BTSerial.print(arduino_num);
  BTSerial.print(":");
  BTSerial.print(h); BTSerial.print(" ");
  BTSerial.print(t); BTSerial.print(" ");
  BTSerial.print(cds); BTSerial.print(" ");
  BTSerial.print(dus); BTSerial.print(" ");
  BTSerial.print(LED_STATUS); BTSerial.print("!");

  delay(5000);

  //BluetoothSerial Read
  while (BTSerial.available() > 0) {
    char msg = (char)BTSerial.read();
    
    if (msg == '1'){
      LED_STATUS = 1;
    } else {
      LED_STATUS = 0;
    }
  }
}
