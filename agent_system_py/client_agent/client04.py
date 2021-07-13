import socket
from select import *
import sys
import bluetooth
import json
import client_dust04_sensor
import client_dust04_actuator

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
    print("Server Host Actuator : ", HOST, " | Port : ", PORT_ACTUATOR)
    print("Bluetooth Address : ", BT_ADDR, "Port : ", BT_PORT)

    # Bluetooth Socket
    bt_s=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    bt_s.connect((BT_ADDR,BT_PORT))
    
    client_sensor = client_dust04_sensor.client_dust04_sensor(bt_s, HOST, SYSTEM_ID, PORT_SENSOR)
    client_actuator = client_dust04_actuator.client_dust04_actuator(bt_s, HOST, SYSTEM_ID, PORT_ACTUATOR)
    
    client_sensor.start()
    client_actuator.start()
    
    client_sensor.join()
    client_actuator.join()
    
    bt_s.close()
