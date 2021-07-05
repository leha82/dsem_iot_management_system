import json
import threading
import DBManager
import SensorCollector

if __name__ == "__main__":
    file_path = './server_agent/config.json'
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        server_ip = fd['SERVER_IP']
        port_sensor = fd['PORT_Sensor']
        port_actuator = fd['PORT_Actuator']
        db_host = fd['DB_Host']
        db_user = fd['DB_User']
        db_pw = fd['DB_Password'] 
        dbn_dr = fd['DBName_Registry']
        dbn_measure = fd['DBName_Measurement']
        tbl_specific = fd['TblName_SpecificMetadata']
        tbl_dl = fd['TblName_DeviceList']

    print(server_ip)
    dbm = DBManager.DBManager(db_host, db_user, db_pw, dbn_dr, dbn_measure, tbl_specific, tbl_dl)
    dbm.DB_Con()
#    server = TcpServer.TcpServer()
    sensor_collector = SensorCollector.SensorCollector(dbm, server_ip, port_sensor)
    sensor_collector.start()
    sensor_collector.join()
