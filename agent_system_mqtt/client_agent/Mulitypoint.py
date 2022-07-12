import socket
from select import *
import sys
import bluetooth
import json
import paho.mqtt.client as mqtt
import SensorPublisher as sp
import ActuatorSubscriber as AS



if __name__ == "__main__":
    file_path = './config.json'
    blue_config_path= 'ble_config.json'
    BTList=[]
    systemIdList=[]
    MQTT_BROKER_IP=""
    BT_PORT=1

    with open(file_path, "r") as fj:
        fd = json.load(fj)
        MQTT_BROKER_IP = fd['MQTT_BROKER_IP']
        #BT_ADDR = fd['BT_ADDR']
        #BT_PORT = fd['BT_PORT']
        #SYSTEM_ID = fd['SYSTEM_ID']
    with open(blue_config_path, "r") as _blue:
        bleConJson= json.load(_blue)
        #BT_PORT= bleConJson['BT_PORT']
        for _ in bleConJson["BT_ADDR"]:
            BTList.append(_)
        for _ in bleConJson['SYSTEM_ID']:
            systemIdList.append(_)
    # print("Server Host Sensor : ", HOST, " | Port : ", PORT_SENSOR)
    # print("Server Host Actuator : ", HOST, " | Port : ", PORT_ACTUATOR)
    print("MQTT Broker HOST : ", MQTT_BROKER_IP)
    #print("System ID : ", SYSTEM_ID)
    for BT_ADDR in BTList:
        print("Bluetooth Address : ", BT_ADDR, "Port : ", BT_PORT)

    bt_sockets=[]
    sensor_publishers=[]
    actuator_subscribers=[]
    for _ in range(len(BTList)):
        print(_)
        bt_sockets.append(bluetooth.BluetoothSocket(bluetooth.RFCOMM))
        bt_sockets[_].connect((BTList[_],BT_PORT))

        sensor_publishers.append(sp.SensorPublisher(bt_sockets[_], MQTT_BROKER_IP,systemIdList[_]))
        actuator_subscribers.append(AS.ActuatorSubscriber(bt_sockets[_], MQTT_BROKER_IP,systemIdList[_]))
        sensor_publishers[_].start()
        actuator_subscribers[_].start()


    for _ in range(len(BTList)):
        sensor_publishers[_].join()
        actuator_subscribers[_].join()

        bt_sockets[_].close()
    
    
    

    