import socket 
from select import * 
import sys 
import bluetooth 
import json 
import datetime 
from time import sleep 
import threading
import paho.mqtt.client as mqtt
 
BUFFSIZE=1024 
 
class client_actuator(threading.Thread):
    def __init__(self, bt_socket, HOST, SYSTEM_ID, PORT_ACTUATOR, MQTT_BROKER_HOST): 
        threading.Thread.__init__(self) 
        self.bt_socket = bt_socket 
        self.HOST = HOST 
        self.SYSTEM_ID = SYSTEM_ID 
        self.PORT_ACTUATOR = PORT_ACTUATOR
        self.MQTT_BROKER_HOST = MQTT_BROKER_HOST
    
    
    # MQTT function
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, client, userdata, msg):
        receive_data = str(msg.payload.decode("utf-8"))
        print("received message = ", receive_data)
        # received message >> actuator:status 
        self.bt_socket.send(receive_data)      
 
        
    def run(self):   
             
        while True:
            # New Client Create
            client = mqtt.Client()
            # Callback function settings... on_connect(Connection to Broker), on_disconnect(Disconnect to Broker), on_subscribe(topic subscribe),
            # on_message(When a published message is received)
            client.on_connect = self.on_connect
            client.on_disconnect = self.on_disconnect
            client.on_subscribe = self.on_subscribe
            client.on_message = self.on_message

            client.connect(self.MQTT_BROKER_HOST, 1883)
            
            client.subscribe('data/actuator', 1)
            client.loop_forever()

            #client.disconnect()
