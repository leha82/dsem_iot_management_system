import json
import threading
import DBManager
import SensorCollector
import ActuatorController

def printConfig(mqtt_broker_ip, db_host, db_port, db_user, db_pw, dbn_dr, dbn_measure, tbl_specific, tbl_dl):
    print("mqtt_broker_ip ", mqtt_broker_ip)
    print("db_host ", db_host)
    print("db_port ", db_port)
    print("db_user ", db_user)
    print("db_pw ", db_pw)
    print("dbn_dr ", dbn_dr)
    print("dbn_measure ", dbn_measure)
    print("tbl_specific ", tbl_specific)
    print("tbl_dl ", tbl_dl)


if __name__ == "__main__":
    file_path = './agent_system_mqtt/server_agent/config.json'
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        mqtt_broker_ip = fd['MQTT_BROKER_IP']
        db_host = fd['DB_Host']
        db_port = fd['DB_Port']
        db_user = fd['DB_User']
        db_pw = fd['DB_Password'] 
        dbn_dr = fd['DBName_Registry']
        dbn_measure = fd['DBName_Measurement']
        tbl_specific = fd['TblName_SpecificMetadata']
        tbl_dl = fd['TblName_DeviceList']

    #printConfig(mqtt_broker_ip, db_host, db_port, db_user, db_pw, dbn_dr, dbn_measure, tbl_specific, tbl_dl)
    # print(server_ip)
    dbm = DBManager.DBManager(db_host, db_port, db_user, db_pw, dbn_dr, dbn_measure, tbl_specific, tbl_dl)
    dbm.DB_Con()

    sensor_collector = SensorCollector.SensorCollector(dbm, mqtt_broker_ip)
    # actuator_collector = ActuatorController.ActuatorController(dbm, mqtt_broker_ip)
    
    sensor_collector.start()
    # actuator_collector.start()

    # actuator_collector.join()
    sensor_collector.join()  
