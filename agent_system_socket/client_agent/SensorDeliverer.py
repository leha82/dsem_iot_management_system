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
        print(frontstr, "send to server : ", message)

    def tcpReceive(self, client_socket):
        recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8")
        print(frontstr, "receive from server : ", recv_msg)
        return recv_msg

    def run(self):
        send_data=""

        # while True:
        #     try:

        try:
            loop = True
            while loop:

                # Receive message from bluetooth
                recv_string = ""
                
                while True:
                    recv_msg = self.bt_socket.recv(BUFFSIZE).decode()
                    recv_string = recv_string + recv_msg
                    
                    if recv_string[len(recv_string)-1] == "}": 
                        break
                
                jsondata = json.loads(recv_string)
                print(frontstr, "receive from bluetooth : ", jsondata)
                #print(type(jsondata))
                # add system_id to json object
                jsondata["system_id"] = self.SYSTEM_ID

                print(frontstr, "Connecting server ... ", end="")
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((self.HOST, self.PORT_SENSOR))

                print("Success!!")
        
                # self.tcpSend(client_socket, self.SYSTEM_ID)
                # recv_msg = self.tcpReceive(client_socket)
        
                # Send data
                send_data = json.dumps(jsondata) # dict -> string
                self.tcpSend(client_socket, send_data)
                recv_msg = self.tcpReceive(client_socket)

                if recv_msg == "notreg":
                    print(frontstr, self.SYSTEM_ID, " : Device is not registered!")
                    loop = False
                elif recv_msg == "accept":
                    print(frontstr, "Sensor data is stored.")
                else:
                    print(frontstr, recv_msg, ": Message is not defined")

            # while-try style
            # except KeyboardInterrupt:
            #     print(frontstr, "Client stopped")
            #     break;
            # except Exception as e :
            #     print(frontstr, "error > ", e)

        # try-while style
        except KeyboardInterrupt:
            print(frontstr, "Sensor Deliverer is stopped")
        except Exception as e :
            print(frontstr, "Error is occured : ", e)


        client_socket.close()
        print(frontstr, "Closing socket server")

   

