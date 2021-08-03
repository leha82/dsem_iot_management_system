import socket
from select import *
import sys
import datetime
import threading
import json
import paho.mqtt.client as mqtt

BUFFSIZE=1024

class SensorPublisher(threading.Thread):
    def __init__(self, bt_socket, HOST, SYSTEM_ID, PORT_SENSOR, MQTT_BROKER_HOST):
        threading.Thread.__init__(self)
        self.bt_socket = bt_socket
        self.HOST = HOST
        self.SYSTEM_ID = SYSTEM_ID
        self.PORT_SENSOR = PORT_SENSOR
        self.MQTT_BROKER_HOST = MQTT_BROKER_HOST

    def on_connect(self, client, userdata, flags, rc):
        # 연결이 성공적으로 된다면 완료 메세지 출력
        if rc == 0:
            print("completely connected")
        else:
            print("Bad connection Returned code=", rc)
    
    # 연결이 끊기면 출력
    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))
    
    def on_publish(self, client, userdata, mid):
        print("In on_pub callback mid= ", mid)
    
    
    def run(self):
        # 새로운 클라이언트 생성
        client = mqtt.Client()
        # 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_publish(메세지 발행)
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_publish = self.on_publish
        
        send_data=""

        while True:
            # 블루투스로 데이터 먼저 받고 -> 소켓 연결 -> 데이터 전송        
            # 1. 블루투스로 데이터 전달 받기
            recv_string = ""
            
            while True:
                # 아두이노에서 json형태로 변환할 수 있을지 확인해 볼 것. 
                # 아두이노에서 system id 도 함께 보내줄 수 있도록
                recv_msg = self.bt_socket.recv(BUFFSIZE).decode()
                recv_string = recv_string + recv_msg
                
                if recv_string[len(recv_string)-1] == "}":  # 수정 : 특수문자(종료문자)붙여서 보내기 
                    break
            
            jsondata = json.loads(recv_string)
            #print(type(jsondata))
            print(jsondata)
            
            SYSTEM_ID = jsondata["system_id"]
            send_data = json.dumps(jsondata)
            #print("systemID", SYSTEM_ID)
            

            # 로컬 아닌, 원격 mqtt broker에 연결
            # address : broker.hivemq.com
            # port: 1883 에 연결
            # 라즈베리파이 자신에게 MQTT 브로커가 설치되어 있으므로 자신의 IP를 넣어줌
            client.connect('203.234.62.117', 1883)
            client.loop_start()
            # 'test/hello' 라는 topic 으로 메세지 발행
            client.publish('test/sensor', send_data, 1)
            client.loop_stop()
            # 연결 종료
            client.disconnect()

   

