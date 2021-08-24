#include <ArduinoJson.h>

// servo motor setting
#include <Servo.h>  
Servo myservo;   
int SERVO_PIN = 9;
int servo_status = 0;

#include <SoftwareSerial.h>
SoftwareSerial BTSerial(A5,A4); // Tx, Rx

// Device Number
String system_id = "DSEM_EIC151_0001";

// Device perperty
int LOOP_DELAY = 500;         // delay time per one loop (milli second)
int SENSING_TIME = 4000;      // sensing duration (mili second)
//int ACTUATION_TIME = 1000;    //actuation duration
int curr_time = 0;            // curr_time will increase LOOP_DELAY after one loop
 
void setup() {
  // initialize communication 
  Serial.begin(9600);     
  BTSerial.begin(9600);
  myservo.attach(SERVO_PIN); 
  myservo.write(0);
}

void loop() {
  while (BTSerial.available() > 0) {
      String recv = BTSerial.readString();
      Serial.print("receive:");
      Serial.println(recv);    // ex) servo:130
  
      int index1 = recv.indexOf(':');
      int index2 = recv.length();
      String actuator = recv.substring(0, index1);  
      String value = recv.substring(index1+1, index2);
      Serial.print(actuator);
      Serial.print("->");
      Serial.println(value);
  
      if (actuator == "servomotor") {
        servo_status = value.toInt();
        myservo.write(servo_status);
      }
    }
    

  // send sensing data to raspberry pi per 5 sec
  if(curr_time >= SENSING_TIME) {

    // create sensor message in json and send it format using bluetooth module
    String jsondata = "";

    StaticJsonDocument<200> doc;

    doc["system_id"] = system_id;
    doc["servomotor"] = servo_status;

    serializeJson(doc, Serial);
    serializeJson(doc, BTSerial);

    Serial.println();  
    curr_time = 0;
  } 
  curr_time += LOOP_DELAY;
  delay(LOOP_DELAY);
}
