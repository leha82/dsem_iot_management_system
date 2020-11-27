#include <SoftwareSerial.h>

SoftwareSerial BTSerial(2,3); // Tx, Rx

// DHT11 Settings...
#include "DHT.h"           
#define DHTPIN 7                
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// DusrSensor Settings...
int LED = 11;
int DUST = 0;
int samplingTime = 280;
int deltaTime = 40;
int sleepTime = 9680;
float dustval = 0;
float voltage = 0;
float dustug = 0;
float dus = 0;
float a = 0;

// cds Settings...
int cds = 0;

// Device Number
String arduino_num = "02";

void setup() {
  Serial.begin(9600);        // 시리얼 통신 시작
  pinMode(LED, OUTPUT);  // 먼지센서 LED 핀 설정
  BTSerial.begin(9600); // 블루투스 시리얼 개방
}

void loop() {
  // DustSensor code
  digitalWrite(LED, LOW); // 적외선 LED ON
  delayMicroseconds(samplingTime);
  dustval = analogRead(DUST); //먼지센서 값 읽기
  delayMicroseconds(deltaTime);
  digitalWrite(LED, HIGH); // 적외선 LED OFF
  delayMicroseconds(sleepTime);
  voltage = dustval * (5.0 / 1024.0);  // 전압 구하기, 전압 단위 : V
  dustug = 0.17 * voltage;      // ug 단위 변환
  dus = dustug * 1000;

  // dht11 code
  int h = dht.readHumidity(); 
  int t = dht.readTemperature();

  // cds code
  cds = analogRead(A2);

  // BluetoothSerial print
  BTSerial.print(arduino_num);
  BTSerial.print(":");
  BTSerial.print(h); BTSerial.print(" ");
  BTSerial.print(t); BTSerial.print(" ");
  BTSerial.print(cds); BTSerial.print(" ");
  BTSerial.print(dus); BTSerial.print("!");

  // Serial Monitor
  Serial.print(arduino_num);
  Serial.print(":");
  Serial.print(h); Serial.print(" ");
  Serial.print(t); Serial.print(" ");
  Serial.print(cds); Serial.print(" ");
  Serial.print(dus); Serial.print("!");
  Serial.println();

  delay(5000);
}
