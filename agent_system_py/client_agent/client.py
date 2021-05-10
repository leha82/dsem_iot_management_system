import socket
from select import *
import sys
import time
import bluetooth
import TcpNet
import datetime

HOST = "203.234.62.109"
PORT = 11201
BUFSIZE=1024

bt_addr="98:D3:71:FD:7D:59"
bt_port=1

# 아두이노 데이터 받기위한 블루투스 소켓
bt_s=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
bt_s.connect((bt_addr,bt_port))
send_data=""
cnt=0
recv_list=[]
Tcp= TcpNet.TcpNet()
Tcp.Connect(HOST,PORT)
system_id = 'device0004'

def format_data(msg):
    msg_list = msg.split(" ")
    
    humi = "humidity:" + msg_list[0]
    temp = "temperature:" + msg_list[1]
    cds = "light:" + msg_list[2]
    
    result = humi + "!" + temp + "!" + cds
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_data = date + "!" + result
    print(send_data)
    return send_data

while True:
    Tcp.SendStr(system_id)
        
    if Tcp.ReceiveStr() == "yes":
        break;
    elif Tcp.ReceiveStr() == "no":
        print(">> 등록되지 않은 기기입니다!")
        sys.exit(0)
while True:
    try:
        recv_string = ""
        arduino_num=""
        recv_data=""
        while True:
            recv_msg = bt_s.recv(BUFSIZE).decode()
            recv_string = recv_string + recv_msg
            
            if recv_string[len(recv_string)-1] == "!":
                break
        
        arduino_num = recv_string.split(":")[0]
        recv_data = recv_string.split(":")[1]
        recv_data = recv_data.replace("!","")
        print(arduino_num)
        print(recv_data)
        
        send_data = format_data(recv_data)
        # 서버로 데이터 전송하기 위한 소켓
        Tcp.SendStr('send')
        if(Tcp.ReceiveStr()=='con'):
            Tcp.SendStr(send_data)
        
    except KeyboardInterrupt:
        
        Tcp.SendStr("exit")
        break
bt_s.close()
Tcp.Close()