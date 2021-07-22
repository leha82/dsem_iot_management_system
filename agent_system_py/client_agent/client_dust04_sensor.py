import socket
from select import *
import sys
import datetime
import threading
import json

BUFFSIZE=1024

class client_sensor(threading.Thread):
    def __init__(self, bt_socket, HOST, SYSTEM_ID, PORT_SENSOR):
        threading.Thread.__init__(self)
        self.bt_socket = bt_socket
        self.HOST = HOST
        self.SYSTEM_ID = SYSTEM_ID
        self.PORT_SENSOR = PORT_SENSOR

    # json 형태로 변환
    def format_data(self, msg):
        msg_list = msg.split(" ")
        
        humi = msg_list[0]
        temp = msg_list[1]
        cds = msg_list[2]
        dust = msg_list[3]
        led = msg_list[4]
        
        result = humi + "!" + temp + "!" + cds + "!" + dust + "!" + led
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        send_data = date + "!" + result
        print(send_data)
        return send_data

    def tcpSend(self, client_socket, message):
        client_socket.send(bytes(message,"UTF-8"))
        #print("[sensor] tcp send : ", message)

    def tcpReceive(self, client_socket):
        recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8")
        #print("[sensor] tcp receive : ", recv_msg)
        return recv_msg

    def run(self):
        send_data=""

        while True:
            # 블루투스로 데이터 먼저 받고 -> 소켓 연결 -> 데이터 전송        
            try:
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
                
                self.SYSTEM_ID = jsondata["system_id"]
                
                # 2. 소켓 연결
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((self.HOST, self.PORT_SENSOR))
        
                while True:
                    self.tcpSend(client_socket, self.SYSTEM_ID)
                    recv_msg = self.tcpReceive(client_socket)
        
                    if recv_msg == "yes":
                        break
                    elif recv_msg == "no":
                        print(">> This device is not registered!")
                        sys.exit(0)
            
                # 3. 데이터 전송
                send_data = json.dumps(jsondata) # dict -> string
                self.tcpSend(client_socket, send_data)
                
            except KeyboardInterrupt:
                print("Client stopped")
                break
            except :
                print("TCP protocol error")
            
            print("connection again")


        client_socket.close()
   
