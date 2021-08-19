import socket
from select import *
import sys
import datetime
import threading
import json
import paho.mqtt.client as mqtt

BUFFSIZE=1024

class SensorPublisher(threading.Thread):
    def __init__(self, bt_socket, MQTT_BROKER_IP, SYSTEM_ID):
    # def __init__(self, bt_socket, HOST, PORT_SENSOR, MQTT_BROKER_HOST, SYSTEM_ID):
        threading.Thread.__init__(self)
        self.bt_socket = bt_socket
        # self.HOST = HOST
        # self.PORT_SENSOR = PORT_SENSOR
        self.broker_ip = MQTT_BROKER_IP
        self.system_id = SYSTEM_ID

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("completely connected")
        else:
            print("Bad connection Returned code=", rc)
    
    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))
    
    def on_publish(self, client, userdata, mid):
        print("In on_pub callback mid= ", mid)
    
    
    def run(self):
        # New Client Create
        client = mqtt.Client()
        # Callback function settings... on_connect(Connection to Broker), on_disconnect(Disconnect to Broker), on_publish
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_publish = self.on_publish
        
        send_data=""

        while True:
            # Receive data from Bluetooth -> socket connection -> data send        
            # 1. Receive data from Bluetooth
            recv_string = ""
            
            while True:
                recv_msg = self.bt_socket.recv(BUFFSIZE).decode()
                recv_string = recv_string + recv_msg
                
                if recv_string[len(recv_string)-1] == "}": 
                    break
            
            jsondata = json.loads(recv_string)
            #print(type(jsondata))
            print("received json : ", jsondata)

            jsondata["system_id"] = self.system_id
            print("system_id modified : ", jsondata)
            
            SYSTEM_ID = jsondata["system_id"]
            TOPIC = SYSTEM_ID + "/sensor"
            send_data = json.dumps(jsondata)
            print("System ID : ", SYSTEM_ID)

            
            client.connect(self.broker_ip, 1883)
            client.loop_start()
            client.publish(TOPIC, send_data, 1)
            client.loop_stop()
            client.disconnect()

   

