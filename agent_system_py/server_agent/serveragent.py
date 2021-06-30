import json
import threading
import SensorCollector
import DBManager


if __name__ == "__main__":
    file_path = 'config.json'
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        port_sensor = fd['PORT_Sensor']
        port_actuator = fd['PORT_Actuator']
        db_host = fd['DB_Host']
        db_user = fd['DB_User']
        db_pw = fd['DB_Password'] 
        dbn_dr = fd['DBName_Registry']
        dbn_measure = fd['DBName_Measurement']
        tbl_specific = fd['TblName_SpecificMetadata']
        tbl_dl = fd['TblName_DeviceList']

    dbm = DBManager.DBManager(db_host, db_user, db_pw, dbn_dr, dbn_measure, tbl_specific, tbl_dl)
    dbm.DB_Con()
#    server = TcpServer.TcpServer()
    sensor_collector = SensorCollector.SensorCollector(dbm, 'localhost', port_sensor, port_actuator)

    sensor_thread = threading.Thread(target=SensorCollector.runSensorCollector, args=(sensor_collector))
    #actuator_thread = threading.Thread(target=sensor_collector.actuatorThread, args=())
