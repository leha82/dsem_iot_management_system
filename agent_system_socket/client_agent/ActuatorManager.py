import socket
from select import *
import sys
import bluetooth
import json
import datetime
from time import sleep
import threading

BUFFSIZE=1024

frontstr = "AM >> "

class ActuatorManager(threading.Thread):
    def __init__(self, bt_socket, HOST, PORT_ACTUATOR, SYSTEM_ID):
        threading.Thread.__init__(self)
        self.bt_socket = bt_socket
        self.HOST = HOST
        self.PORT_ACTUATOR = PORT_ACTUATOR
        self.SYSTEM_ID = SYSTEM_ID
            
    def tcpSend(self, client_socket, message):
        client_socket.send(bytes(message,"UTF-8"))
        print(frontstr, "send : ", message)

    def tcpReceive(self, client_socket):
        recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8")
        print(frontstr, "receive : ", recv_msg)
        return recv_msg
    
    def run(self):  
            
        while True:
            try:
                print(frontstr, "try to connect actuator agent of server...")
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((self.HOST, self.PORT_ACTUATOR))

                self.tcpSend(client_socket, self.SYSTEM_ID)
                recv_msg = self.tcpReceive(client_socket)

                if recv_msg != "notreg" and recv_msg != "noevt":
                    # received message >> actuator:status
                    self.bt_socket.send(recv_msg)     
                elif recv_msg == "notreg":
                    print(frontstr, "This device is not registered!")
                elif recv_msg == "noevt":
                    print(frontstr, "There is no event for all actutators")

            except KeyboardInterrupt:
                print(frontstr, "Client stopped")
                break;
            except Exception as e :
                print(frontstr, "error > ", e)

            sleep(5)

        client_socket.close()

