import socket
from select import *
import sys
import datetime
import threading
import json
import paho.mqtt.client as mqtt

BUFFSIZE=1024

class client_sensor(threading.Thread):
    def __init__(self, bt_socket, HOST, SYSTEM_ID, PORT_SENSOR, MQTT_BROKER_HOST):
        threading.Thread.__init__(self)
        self.bt_socket = bt_socket
        self.HOST = HOST
        self.SYSTEM_ID = SYSTEM_ID
        self.PORT_SENSOR = PORT_SENSOR
        self.MQTT_BROKER_HOST = MQTT_BROKER_HOST

    def on_connect(self, client, userdata, flags, rc):
        # Connection Success
        if rc == 0:
            print("completely connected")
        else:
            print("Bad connection Returned code=", rc)
    
    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))
    
    def on_publish(self, client, userdata, mid):
        print("In on_pub callback mid= ", mid)
    
    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, client, userdata, msg):
        receive_data = str(msg.payload.decode("utf-8"))
        print("received message = ", receive_data)

    def run(self):
        # New Client Create
        client = mqtt.Client()
        # Callback function settings... on_connect(Connection to Broker), on_disconnect(Disconnect to Broker), on_publish
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_publish = self.on_publish
        client.on_subscribe = self.on_subscribe
        client.on_message = self.on_message

        
        send_data=""

        while True:
            # Receive data from Bluetooth -> socket connection  -> data send
            # 1. Receive data from Bluetooth
            recv_string = ""
            
            while True:
                recv_msg = self.bt_socket.recv(BUFFSIZE).decode()
                recv_string = recv_string + recv_msg
                
                if recv_string[len(recv_string)-1] == "}": 
                    break
            
            jsondata = json.loads(recv_string)
            #print(type(jsondata))
            print(jsondata)
            
            SYSTEM_ID = jsondata["system_id"]
            send_data = json.dumps(jsondata)
            #print("systemID", SYSTEM_ID)
            
            client.connect(self.MQTT_BROKER_HOST, 1883)
            client.loop_start()
            client.publish('data/sensor', send_data, 1)
            client.loop_stop()

            client.disconnect()

   

