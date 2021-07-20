#include <ArduinoJson.h>

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
String system_id = "device0004";

// actuator status
String msg = "";  
String actuator = "";
int value = 0;

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
//  Serial.print(system_id);
//  Serial.print(":");
//  Serial.print("humidity="); Serial.print(h); Serial.print(" ");
//  Serial.print("temperature="); Serial.print(t); Serial.print(" ");
//  Serial.print("light="); Serial.print(cds); Serial.print(" ");
//  Serial.print("dust="); Serial.print(dus); Serial.print(" ");
//  Serial.print("led="); Serial.print(LED_STATUS); Serial.print("!");
//  Serial.println();

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

  // JSON
  String jsondata = "";

  StaticJsonBuffer<200> jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  root["system_id"] = system_id;
  root["humidity"] = h;
  root["temperature"] = t;
  root["light"] = cds;
  root["dust"] = dus;
  root["led"] = LED_STATUS;

  root.printTo(jsondata);  // String으로 변환
  Serial.println(jsondata);
    
  // BluetoothSerial print
//  BTSerial.print(system_id);
//  BTSerial.print(":");
//  BTSerial.print("humidity="); BTSerial.print(h); BTSerial.print(" ");
//  BTSerial.print("temperature=");BTSerial.print(t); BTSerial.print(" ");
//  BTSerial.print("light=");BTSerial.print(cds); BTSerial.print(" ");
//  BTSerial.print("dust=");BTSerial.print(dus); BTSerial.print(" ");
//  BTSerial.print("led=");BTSerial.print(LED_STATUS); BTSerial.print("!");

  BTSerial.print(jsondata);
  delay(5000);

  //BluetoothSerial Read
  while (BTSerial.available() > 0) {
    String recv = BTSerial.readString();
    //Serial.println(recv);    // ex) led:1

    int index1 = recv.indexOf(':');
    int index2 = recv.length();
    actuator = recv.substring(0, index1);  // led
    value = recv.substring(index1+1, index2).toInt();  // 1
    //Serial.println(value);

    if (actuator == "led") {
      LED_STATUS = value;
    }
  }
}
