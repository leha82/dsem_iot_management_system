import socket
from select import *
import sys
import bluetooth
import json
import client_dust04_sensor as cs
import client_dust04_actuator as ca

# 아두이노에서 데이터 보낼때 컬럼 붙이기

if __name__ == "__main__":
    file_path = 'config.json'
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        HOST = fd['SERVER_IP']
        PORT_SENSOR = fd['SERVER_PORT_SENSOR']
        PORT_ACTUATOR = fd['SERVER_PORT_ACTUATOR']
        BT_ADDR = fd['BT_ADDR']
        BT_PORT = fd['BT_PORT']
        SYSTEM_ID = fd['SYSTEM_ID']

    print("System ID : ", SYSTEM_ID)
    print("Server Host Sensor : ", HOST, " | Port : ", PORT_SENSOR)
    #print("Server Host Actuator : ", HOST, " | Port : ", PORT_ACTUATOR)
    print("Bluetooth Address : ", BT_ADDR, "Port : ", BT_PORT)

    # Bluetooth Socket
    bt_socket=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    bt_socket.connect((BT_ADDR,BT_PORT))
    
    sensor = cs.client_sensor(bt_socket, HOST, SYSTEM_ID, PORT_SENSOR)
    #actuator = ca.client_actuator(bt_socket, HOST, SYSTEM_ID, PORT_ACTUATOR)
    
    sensor.start()
    #actuator.start()
    
    sensor.join()
    #actuator.join()
    
    bt_socket.close()
