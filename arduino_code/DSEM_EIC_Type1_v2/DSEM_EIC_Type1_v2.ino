#include <ArduinoJson.h>

//1602 LCD Setting
#include <LiquidCrystal.h>               // LCD libaray
LiquidCrystal lcd(13, 12, 5, 4, 3, 2);   // LCD pin setting

#include <SoftwareSerial.h>
SoftwareSerial BTSerial(A5,A4); // Tx, Rx <- user analog pin as digital output

// DHT11 Settings...
#include "DHT.h"           
#define DHTPIN 7                
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Device Number
String system_id = "DSEM_EIC01_0001";

// Device perperty
int LOOP_DELAY = 500;         // delay time per one loop (milli second)
int SENSING_TIME = 5000;      // sensing duration (mili second)
int ACTUATION_TIME = 1000;    //actuation duration
int curr_time = 0;            // curr_time will increase LOOP_DELAY after one loop

// 1602 LCD setting
int LCDLIGHT_PIN = 6;

// Dust Sensor Setting
int DUSTLED_PIN = 8;
int DUST_PIN = A0;
int samplingTime = 280;
int deltaTime = 40;
int sleepTime = 9680;
float dust = 0;

// LED light setting
int LEDRED_PIN = 11;
int LEDGREEN_PIN = 10;
int LEDBLUE_PIN = 9;
int led_red = 255;
int led_green = 255;
int led_blue = 255;
int led_status = 1;

// cds Settings...
int cds = 0;
int CDS_PIN = A2;


void setup() {
  // initialize communication 
  Serial.begin(9600);        
  BTSerial.begin(9600); 
  
  // initialize sensor

  // initialize actuator
  pinMode(DUSTLED_PIN, OUTPUT);    // set led pin of dust sensor.
    
  pinMode(LEDRED_PIN, OUTPUT);     // set rgb led light value
  pinMode(LEDGREEN_PIN, OUTPUT);
  pinMode(LEDBLUE_PIN, OUTPUT);
  
  pinMode(LCDLIGHT_PIN, OUTPUT);   // initialization of 16x2 LCD 
  analogWrite(LCDLIGHT_PIN, 120);
  lcd.begin(16, 2);
}

void loop() {
  // one loop has 0.5 sec delay
  // sensing per 5 sec, actuating per 1 sec

  if (curr_time % ACTUATION_TIME == 0) {
//    Serial.print("check actuation : "); Serial.println(curr_time); 
    // BluetoothSerial Read as json format
    while (BTSerial.available() > 0) {
      String recv = BTSerial.readString();
      Serial.print("receive:");
      Serial.println(recv);    // ex) led:1
  
      int index1 = recv.indexOf(':');
      int index2 = recv.length();
      String actuator = recv.substring(0, index1);  
      String value = recv.substring(index1+1, index2);
      //Serial.println(value);
  
      if (actuator == "led") {
        led_status = value.toInt();
      }
    }
  }

  // read DustSensor
  digitalWrite(DUSTLED_PIN, LOW); 
  delayMicroseconds(samplingTime);
  float dustval = analogRead(DUST_PIN); 
  delayMicroseconds(deltaTime);
  digitalWrite(DUSTLED_PIN, HIGH);
  delayMicroseconds(sleepTime);
  float voltage = dustval * (5.0 / 1024.0);    // voltage unit : V
  float dustug = 0.17 * voltage;               // change voltage into micro gram (ug)
  float dustmg = dustug * 1000;                // change dust unit (ug) into milligram (mg)
  
  if (dustmg > 0) dust = dustmg;               // if the dustmg is negative value, dust is not changed

  int disp_dust = (int)dustmg;                 // display value for lcd pannel

  // read dht11
  int humi = dht.readHumidity(); 
  int temp = dht.readTemperature();

  // read cds
  cds = analogRead(CDS_PIN);

  // send sensing data to raspberry pi per 5 sec
  if(curr_time % SENSING_TIME == 0) {
    //Display to 1602 LCD module
    lcd.clear();
  
    lcd.setCursor(0, 0);
    lcd.print("H:");  lcd.print(humi);  lcd.print("%");
    
    lcd.setCursor(8, 0);
    lcd.print("T:");  lcd.print(temp);  lcd.print("C");
    
    lcd.setCursor(0, 1);
    lcd.print("D:");  lcd.print(disp_dust);  lcd.print("ug");
    
    lcd.setCursor(8, 1);
    lcd.print("L:");  lcd.print(cds);
  
    // LED Light Change
    led_red = 0;  led_green = 0;  led_blue = 0;
    if (led_status==1) {
      if (dust < 35) {           // air quality is good : blue light
        led_red = 0;  led_green = 0;  led_blue = 255;
      } else if (dust < 70) {    // air quality is normal : green light
        led_red = 0;  led_green = 255;  led_blue = 0;
      } else if (dust >= 100) {  // air quality is good : red light
        led_red = 255;  led_green = 0;  led_blue = 0;
      }
    }
    analogWrite(LEDRED_PIN, led_red);
    analogWrite(LEDGREEN_PIN, led_green);
    analogWrite(LEDBLUE_PIN, led_blue);
    
    // create sensor message in json and send it format using bluetooth module
    String jsondata = "";

    StaticJsonDocument<200> doc;
//    JsonObject root = doc.to<JsonObject>();

//  doc["system_id"] = system_id;
    doc["humidity"] = humi;
    doc["temperature"] = temp;
    doc["light"] = cds;
    doc["dust"] = dust;
    doc["led"] = led_status;

    serializeJson(doc, Serial);
    serializeJson(doc, BTSerial);

    Serial.println();
    
//    root.printTo(jsondata);  // change jsonobject to String
//    Serial.println(jsondata);
//    BTSerial.print(jsondata);
    
    curr_time = 0;
  }
  
  curr_time += LOOP_DELAY;
  
  delay(LOOP_DELAY);
}
