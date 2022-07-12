import socket
from select import *
import string
import sys
import bluetooth as bt
import json
import paho.mqtt.client as mqtt
import SensorPublisher as sp
import ActuatorSubscriber as AS



if __name__ == "__main__":
    file_path = './config.json'
    blue_config_path= 'ble_config.json'
    BTList=[]
    BT_PORT=1
    SYSTEM_ID="testdevice01"
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        MQTT_BROKER_IP = fd['MQTT_BROKER_IP']
        #BT_ADDR = fd['BT_ADDR']
        #BT_PORT = fd['BT_PORT']
        #SYSTEM_ID = fd['SYSTEM_ID']
    with open(blue_config_path, "r") as _blue:
        bleConJson= json.load(_blue)
        #BT_PORT= bleConJson["BT_PORT"]
        for _ in bleConJson["BT_ADDR"]:
            BTList.append(_)
    # print("Server Host Sensor : ", HOST, " | Port : ", PORT_SENSOR)
    # print("Server Host Actuator : ", HOST, " | Port : ", PORT_ACTUATOR)
    print("MQTT Broker HOST : ", MQTT_BROKER_IP)
    #print("System ID : ", SYSTEM_ID)
    for BT_ADDR in BTList:
        print("Bluetooth Address : ", BT_ADDR, "Port : ", BT_PORT)
    
    bt_socket=bt.BluetoothSocket(bt.RFCOMM)
    print("{0}, {1}".format("20:13:06:18:10:53",BT_PORT))
    
    bt_socket.connect(("20:13:06:18:10:53",1))
    sensor = sp.SensorPublisher(bt_socket, MQTT_BROKER_IP,SYSTEM_ID)
    actuator = AS.ActuatorSubscriber(bt_socket, MQTT_BROKER_IP, SYSTEM_ID)
    
    sensor.start()
    actuator.start()

    sensor.join()    
    actuator.join()
    
    bt_socket.close()
    

    