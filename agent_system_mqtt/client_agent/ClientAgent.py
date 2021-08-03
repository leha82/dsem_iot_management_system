import socket
from select import *
import sys
import bluetooth
import json
import paho.mqtt.client as mqtt
import SensorPublisher as sp
#import ActuatorSubscriber as as

# 아두이노에서 데이터 보낼때 컬럼 붙이기

if __name__ == "__main__":
    file_path = 'config.json'
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        HOST = fd['SERVER_IP']
        PORT_SENSOR = fd['SERVER_PORT_SENSOR']
        PORT_ACTUATOR = fd['SERVER_PORT_ACTUATOR']
        MQTT_BROKER_HOST = fd['MQTT_BROKER_IP']
        BT_ADDR = fd['BT_ADDR']
        BT_PORT = fd['BT_PORT']
        SYSTEM_ID = fd['SYSTEM_ID']

    print("System ID : ", SYSTEM_ID)
    print("Server Host Sensor : ", HOST, " | Port : ", PORT_SENSOR)
    print("Server Host Actuator : ", HOST, " | Port : ", PORT_ACTUATOR)
    print("Bluetooth Address : ", BT_ADDR, "Port : ", BT_PORT)
    print("MQTT Broker HOST : ", MQTT_BROKER_HOST)

    # Bluetooth Socket
    bt_socket=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    bt_socket.connect((BT_ADDR,BT_PORT))
    
    sensor = sp.SensorPublisher(bt_socket, HOST, SYSTEM_ID, PORT_SENSOR, MQTT_BROKER_HOST)
    #actuator = as.ActuatorSubscriber(bt_socket, HOST, SYSTEM_ID, PORT_ACTUATOR)
    
    sensor.start()
    #actuator.start()
    
    #actuator.join()
    sensor.join()
    
    bt_socket.close()

