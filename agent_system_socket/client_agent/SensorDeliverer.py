import socket
from select import *
import sys
import datetime
import threading
import json

BUFFSIZE=1024

frontstr = "SD >> "

class SensorDeliverer(threading.Thread):
    def __init__(self, bt_socket, HOST, PORT_SENSOR, SYSTEM_ID):
        threading.Thread.__init__(self)
        self.bt_socket = bt_socket
        self.HOST = HOST
        self.PORT_SENSOR = PORT_SENSOR
        self.SYSTEM_ID = SYSTEM_ID

    def tcpSend(self, client_socket, message):
        client_socket.send(bytes(message,"UTF-8"))
        print(frontstr, "send : ", message)

    def tcpReceive(self, client_socket):
        recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8")
        print(frontstr, "receive : ", recv_msg)
        return recv_msg

    def run(self):
        send_data=""

        # while True:
        #     try:

        try:
            while True:

                # Receive message from bluetooth
                recv_string = ""
                
                while True:
                    recv_msg = self.bt_socket.recv(BUFFSIZE).decode()
                    recv_string = recv_string + recv_msg
                    
                    if recv_string[len(recv_string)-1] == "}": 
                        break
                
                jsondata = json.loads(recv_string)
                #print(type(jsondata))
                print(frontstr, "Bluetooth : ", jsondata)
                
                jsondata["system_id"] = self.SYSTEM_ID
                
                print(frontstr, "try to connect sensor collector...")
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((self.HOST, self.PORT_SENSOR))

                print(frontstr, "connection success!")
        
                # while True:
                self.tcpSend(client_socket, self.SYSTEM_ID)
                recv_msg = self.tcpReceive(client_socket)
    
                if recv_msg == "yes":
                    break
                elif recv_msg == "no":
                    print(frontstr, "This device is not registered!")
                    sys.exit(0)
            
                # Send data
                send_data = json.dumps(jsondata) # dict -> string
                self.tcpSend(client_socket, send_data)

            # while-try style
            # except KeyboardInterrupt:
            #     print(frontstr, "Client stopped")
            #     break;
            # except Exception as e :
            #     print(frontstr, "error > ", e)

        # try-while style
        except KeyboardInterrupt:
            print(frontstr, "Client stopped")
        except Exception as e :
            print(frontstr, "error > ", e)


        client_socket.close()
        self.bt_socket.close()
        print(frontstr, "close client socket")

   

