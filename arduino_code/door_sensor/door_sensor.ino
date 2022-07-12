#include <ArduinoJson.h>

#include <SoftwareSerial.h>
SoftwareSerial BTSerial(A5,A4); // Tx, Rx <- user analog pin as digital output


// infrared ray
int infrared = 7;

void setup(){
    pinMode(infrared,INPUT);
    Serial.begin(9600);
}


void loop(){
    int state = digitalRead(infrared);

    Serial.print("infrared=");
    Serial.print(state);
}