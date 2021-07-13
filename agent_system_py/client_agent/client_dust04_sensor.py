import socket
from select import *
import sys
import bluetooth
import json
import datetime
import threading

BUFFSIZE=1024

# bt_addr="20:16:12:22:21:76"
# bt_port=1

class client_dust04_sensor(threading.Thread):
    def __init__(self, bt_s, HOST, SYSTEM_ID, PORT_SENSOR):
        threading.Thread.__init__(self)
        self.bt_s = bt_s
        self.HOST = HOST
        self.SYSTEM_ID = SYSTEM_ID
        self.PORT_SENSOR = PORT_SENSOR

    def format_data(self, msg):
        msg_list = msg.split(" ")
        
        humi = "humidity:" + msg_list[0]
        temp = "temperature:" + msg_list[1]
        cds = "light:" + msg_list[2]
        dust = "dust:" + msg_list[3]
        led = "led:" + msg_list[4]
        
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
        cnt=0
        recv_list=[]
        
        while True:
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
                    
            try:
                recv_string = ""
                arduino_num=""
                recv_data=""
                
                while True:
                    recv_msg = self.bt_s.recv(BUFFSIZE).decode()
                    recv_string = recv_string + recv_msg
                    
                    if recv_string[len(recv_string)-1] == "!":
                        break
                
                arduino_num = recv_string.split(":")[0]
                recv_data = recv_string.split(":")[1]
                recv_data = recv_data.replace("!","")
                print(arduino_num)
                print(recv_data)
                
                send_data = self.format_data(recv_data)
                self.tcpSend(client_socket, send_data)
                
            except KeyboardInterrupt:
                print("Client stopped")
                break

        client_socket.close()
   