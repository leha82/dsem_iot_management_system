import socket
from select import *
import sys
import bluetooth
import json
import paho.mqtt.client as mqtt
import SensorPublisher as sp
import ActuatorSubscriber as AS

if __name__ == "__main__":
    file_path = 'config.json'
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        MQTT_BROKER_IP = fd['MQTT_BROKER_IP']
        BT_ADDR = fd['BT_ADDR']
        BT_PORT = fd['BT_PORT']
        SYSTEM_ID = fd['SYSTEM_ID']

    # print("Server Host Sensor : ", HOST, " | Port : ", PORT_SENSOR)
    # print("Server Host Actuator : ", HOST, " | Port : ", PORT_ACTUATOR)
    print("MQTT Broker HOST : ", MQTT_BROKER_IP)
    print("System ID : ", SYSTEM_ID)
    print("Bluetooth Address : ", BT_ADDR, "Port : ", BT_PORT)

    # Bluetooth Socket
    bt_socket=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    bt_socket.connect((BT_ADDR,BT_PORT))
    
    sensor = sp.SensorPublisher(bt_socket, MQTT_BROKER_IP, SYSTEM_ID)
    actuator = AS.ActuatorSubscriber(bt_socket, MQTT_BROKER_IP, SYSTEM_ID)
    
    sensor.start()
    actuator.start()

    sensor.join()    
    actuator.join()
    
    bt_socket.close()

