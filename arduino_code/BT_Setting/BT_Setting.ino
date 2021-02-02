#include <SoftwareSerial.h>
SoftwareSerial BTSerial(8,9); // Tx, Rx

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  BTSerial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (BTSerial.available()) 
    Serial.write(BTSerial.read());
  

  if (Serial.available()) 
    BTSerial.write(Serial.read());
  

  // 실행 후 시리얼 모니터에서
  // BT 접속확인 : AT
  // BT 이름 변경 : AT+NAME변경이름 <-전체 다 붙여야함
  // BT 핀번호 변경 : AT+PIN핀번호
  // BT mac주소 : AT+ADDR
  
}
