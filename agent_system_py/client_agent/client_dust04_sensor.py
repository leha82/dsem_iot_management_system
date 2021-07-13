import socket
from select import *
import sys
import bluetooth
import json
import datetime
from time import sleep

BUFFSIZE=1024

# bt_addr="20:16:12:22:21:76"
# bt_port=1

def tcpSend(client_socket, message):
    client_socket.send(bytes(message,"UTF-8"))
    print("tcp send : ", message)

def tcpReceive(client_socket):
    recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8")
    print("tcp receive : ", recv_msg)
    return recv_msg

if __name__ == "__main__":
    file_path = 'config.json'
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        HOST = fd['SERVER_IP']
        PORT_SENSOR = fd['SERVER_PORT_SENSOR']
        PORT_ACTUATOR = fd['SERVER_PORT_ACTUATOR']
        BT_ADDR = fd['BT_ADDR']
        BT_PORT = fd['BT_PORT']
        SYSTEM_ID = fd['SYSTEM_ID']

    print("System ID : ", SYSTEM_ID)
    print("Server HOST Actuator : ", HOST, " | Port : ", PORT_ACTUATOR)
    print("Bluetooth Address : ", BT_ADDR, "Port : ", BT_PORT)

    # Bluetooth Socket
    bt_s=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    bt_s.connect((BT_ADDR,BT_PORT))
    
    send_data=""
    cnt=0
    recv_list=[]     
    
    while True:
        client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket1.connect((HOST, PORT_ACTUATOR))
        
        
        while True:
            tcpSend(client_socket1, SYSTEM_ID)
            recv_msg = tcpReceive(client_socket1)
        
            if recv_msg == "yes":
                break
            elif recv_msg == "no":
                print("This device is not registered!")
                sys.exit(0)
        
        
        try:
            # actuator:status 
            actmsg = tcpReceive(client_socket1)
            if actmsg == "yesAct":
                msg_act = tcpReceive(client_socket1)
                print(msg_act)
                bt_s.send(msg_act)
            
            sleep(5)
        except KeyboardInterrupt:
            print("Client stopped")
            break

    bt_s.close()
    client_socket1.close()
