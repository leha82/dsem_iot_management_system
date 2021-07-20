#include <ArduinoJson.h>

//1602 LCD Setting
#include <LiquidCrystal.h>               // LCD 라이브러리 포함
LiquidCrystal lcd(13, 12, 5, 4, 3, 2);   // LCD 핀 설정

#include <SoftwareSerial.h>
SoftwareSerial BTSerial(8,9); // Tx, Rx

// DHT11 Settings...
#include "DHT.h"           
#define DHTPIN 7                
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Dust Sensor Setting
int DUST_LED = 11;
int DUST_PIN = 0;
int samplingTime = 280;
int deltaTime = 40;
int sleepTime = 9680;
float dust = 0;
float p_dust = 0;

// LED light setting
int LED_LIGHT = 10;
int LED_STATUS = 0;

// cds Settings...
int cds = 0;

// Device Number
String system_id = "device0004";

void setup() {
  // initialize communication 
  Serial.begin(9600);        // 시리얼 통신 시작
  BTSerial.begin(9600); // 블루투스 시리얼 개방

  // initialize sensor

  // initialize actuator
  pinMode(DUST_LED, OUTPUT);  // 먼지센서 LED 핀 설정
  pinMode(LED_LIGHT, OUTPUT);
  lcd.begin(16, 2);           // 16x2 LCD 선언
}

void loop() {
  // read DustSensor
  digitalWrite(DUST_LED, LOW); // 적외선 LED ON
  delayMicroseconds(samplingTime);
  float dustval = analogRead(DUST_PIN); //먼지센서 값 읽기
  delayMicroseconds(deltaTime);
  digitalWrite(DUST_LED, HIGH); // 적외선 LED OFF
  delayMicroseconds(sleepTime);
  float voltage = dustval * (5.0 / 1024.0);  // 전압 구하기, 전압 단위 : V
  float dustug = 0.17 * voltage;      // ug 단위 변환
  dust = dustug * 1000;

  // read dht11
  int humi = dht.readHumidity(); 
  int temp = dht.readTemperature();

  // read cds
  cds = analogRead(A2);

  // Serial Monitor
//  Serial.print(system_id);
//  Serial.print(":");
//  Serial.print("humidity="); Serial.print(humi); Serial.print(" ");
//  Serial.print("temperature="); Serial.print(temp); Serial.print(" ");
//  Serial.print("light="); Serial.print(cds); Serial.print(" ");
//  Serial.print("dust="); Serial.print(p_dust); Serial.print(" ");
//  Serial.print("led="); Serial.print(LED_STATUS); Serial.print("!");
//  Serial.println();

  //1602 LCD 모듈 코드
  lcd.clear();
  analogWrite(6, 120);
  lcd.setCursor(0, 0);
  lcd.print("H: ");
  lcd.print(humi);
  lcd.print(" %  ");
  lcd.print("T: ");
  lcd.print(temp);
  lcd.print(" C");
  lcd.setCursor(0, 1);
  lcd.print("Dust: ");
  if (dust > 0) {
    p_dust = dust;
    lcd.print(p_dust);
  }
  else {
    lcd.print(p_dust);
  }
  lcd.print("ug");

  // LED Light Change
  digitalWrite(LED_LIGHT, LED_STATUS);
//  if (p_dust < 35) {   // 좋음
//    digitalWrite(10, HIGH);
//  }
//  if (p_dust > 35 & p_dust < 75) {  // 나쁨
//    digitalWrite(10, LOW); delay(1000);
//    digitalWrite(10, HIGH);
//  }
//  if (p_dust > 75) {       // 매우 나쁨
//    digitalWrite(10, LOW); delay(500);
//    digitalWrite(10, HIGH);  
//  }

  // JSON
  String jsondata = "";

  StaticJsonBuffer<200> jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  root["system_id"] = system_id;
  root["humidity"] = humi;
  root["temperature"] = temp;
  root["light"] = cds;
  root["dust"] = p_dust;
  root["led"] = LED_STATUS;

  root.printTo(jsondata);  // String으로 변환
  Serial.println(jsondata);
    
  // BluetoothSerial print
//  BTSerial.print(system_id);
//  BTSerial.print(":");
//  BTSerial.print("humidity="); BTSerial.print(humi); BTSerial.print(" ");
//  BTSerial.print("temperature=");BTSerial.print(temp); BTSerial.print(" ");
//  BTSerial.print("light=");BTSerial.print(cds); BTSerial.print(" ");
//  BTSerial.print("dust=");BTSerial.print(p_dust); BTSerial.print(" ");
//  BTSerial.print("led=");BTSerial.print(LED_STATUS); BTSerial.print("!");

  BTSerial.print(jsondata);

  // BluetoothSerial Read
  // json 형태로 받기
  while (BTSerial.available() > 0) {
    String recv = BTSerial.readString();
    //Serial.println(recv);    // ex) led:1

    int index1 = recv.indexOf(':');
    int index2 = recv.length();
    String actuator = recv.substring(0, index1);  // led
    String value = recv.substring(index1+1, index2);  // 1
    //Serial.println(value);

    if (actuator == "led") {
      LED_STATUS = value.toInt();
    }
  }

  delay(5000);
}
