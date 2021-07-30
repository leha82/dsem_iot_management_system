import socket 
from select import * 
import sys 
import bluetooth 
import json 
import datetime 
from time import sleep 
import threading 
 
BUFFSIZE=1024 
 
class client_actuator(threading.Thread): 
    def __init__(self, bt_socket, HOST, SYSTEM_ID, PORT_ACTUATOR): 
        threading.Thread.__init__(self) 
        self.bt_socket = bt_socket 
        self.HOST = HOST 
        self.SYSTEM_ID = SYSTEM_ID 
        self.PORT_ACTUATOR = PORT_ACTUATOR 
             
    def tcpSend(self, client_socket, message): 
        client_socket.send(bytes(message,"UTF-8")) 
        #print("AA >> send : ", message) 
 
    def tcpReceive(self, client_socket): 
        recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8") 
        #print("AA >> receive : ", recv_msg) 
        return recv_msg 
     
    def run(self):   
             
        while True: 
            try: 
                print("AA >> try to connect actuator agent of server...") 
                client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                client_socket1.connect((self.HOST, self.PORT_ACTUATOR)) 
 
                self.tcpSend(client_socket1, self.SYSTEM_ID) 
                recv_msg = self.tcpReceive(client_socket1) 
 
                if recv_msg == "notreg": 
                    print("AA >> This device is not registered!") 
                elif recv_msg == "noevt": 
                    print("AA >> There is no event for all actutators") 
                else : 
                    # received message >> actuator:status 
                    self.bt_socket.send(recv_msg)      
 
            except KeyboardInterrupt: 
                print("AA >> Client stopped") 
                break 
            except : 
                print("AA >> TCP connection error") 
 
            client_socket1.close() 
            sleep(5)
