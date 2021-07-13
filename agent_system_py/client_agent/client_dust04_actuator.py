import socket
from select import *
import sys
import bluetooth
import json
import datetime
from time import sleep
import threading

BUFFSIZE=1024

class client_dust04_actuator(threading.Thread):
    def __init__(self, bt_s, HOST, SYSTEM_ID, PORT_ACTUATOR):
        threading.Thread.__init__(self)
        self.bt_s = bt_s
        self.HOST = HOST
        self.SYSTEM_ID = SYSTEM_ID
        self.PORT_ACTUATOR = PORT_ACTUATOR
            
    def tcpSend(self, client_socket, message):
        client_socket.send(bytes(message,"UTF-8"))
        #print("[actuator] tcp send : ", message)

    def tcpReceive(self, client_socket):
        recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8")
        #print("[artuator] tcp receive : ", recv_msg)
        return recv_msg
    
    def run(self):
        send_data=""
        cnt=0
        recv_list=[]     
            
        while True:
            client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket1.connect((self.HOST, self.PORT_ACTUATOR))
                
                
            while True:
                self.tcpSend(client_socket1, self.SYSTEM_ID)
                recv_msg = self.tcpReceive(client_socket1)
                
                if recv_msg == "yes":
                    break
                elif recv_msg == "no":
                    print("This device is not registered!")
                    sys.exit(0)
                
            try:
                # actuator:status 
                actmsg = self.tcpReceive(client_socket1)
                if actmsg == "yesAct":
                    msg_act = self.tcpReceive(client_socket1)
                    #print(msg_act)
                    self.bt_s.send(msg_act)
            
                sleep(5)
            except KeyboardInterrupt:
                print("Client stopped")
                break

        client_socket1.close()