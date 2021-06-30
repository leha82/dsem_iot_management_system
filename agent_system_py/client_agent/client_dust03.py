import socket
from select import *
import sys
import bluetooth
import json
import datetime

# HOST = "203.234.62.115"
# PORT = 11201
BUFFSIZE=1024

# bt_addr="20:16:12:22:21:76"
# bt_port=1

def format_data(msg):
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
    print("tcp send : ", message)

def tcpReceive(self, client_socket):
    recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8")
    print("tcp receive : ", recv_msg)
    return recv_msg

if __name__ == "__main__":
    file_path = 'config.json'
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        HOST = fd['SERVER_IP']
        PORT = fd['SERVER_PORT_SENSOR']
        BT_ADDR = fd['BT_ADDR']
        BT_PORT = fd['BT_PORT']
        SYSTEM_ID = fd['SYSTEM_ID']

    print("System ID : ", SYSTEM_ID)
    print("Server Host : ", HOST, " | Port : ", PORT)
    print("Bluetooth Address : ", BT_ADDR, "Port : ", BT_PORT)

    # 아두이노 데이터 받기위한 블루투스 소켓
    # bt_s=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    # bt_s.connect((BT_ADDR,BT_PORT))
    send_data=""
    cnt=0
    recv_list=[]
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
    system_id = 'device0007'

    while True:
        tcpSend(client_socket, system_id)
        recv_msg = tcpReceive(client_socket)
        
        if recv_msg == "yes":
            break;
        elif recv_msg == "no":
            print(">> 등록되지 않은 기기입니다!")
            sys.exit(0)        
    
    while True:
        try:
            recv_string = ""
            arduino_num=""
            recv_data=""
            # while True:
            #     recv_msg = bt_s.recv(BUFFSIZE).decode()
            #     recv_string = recv_string + recv_msg
                
            #     if recv_string[len(recv_string)-1] == "!":
            #         break
            
            arduino_num = recv_string.split(":")[0]
            recv_data = recv_string.split(":")[1]
            recv_data = recv_data.replace("!","")
            print(arduino_num)
            print(recv_data)
            
            send_data = format_data(recv_data)
            # 서버로 데이터 전송하기 위한 소켓
            tcpSend(send_data)
            
        except KeyboardInterrupt:
            print("Client stopped")
            break

    # bt_s.close()
    client_socket.close()

