import json
import threading
import mqtt_DBManager
import mqtt_SensorCollector
import mqtt_ActuatorCollector


if __name__ == "__main__":
    file_path = './agent_system_py/mqtt_system/config.json'
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        server_ip = fd['SERVER_IP']
        port_sensor = fd['PORT_Sensor']
        port_actuator = fd['PORT_Actuator']
        db_host = fd['DB_Host']
        mqtt_broker_host = fd['MQTT_BROKER_HOST']
        db_user = fd['DB_User']
        db_pw = fd['DB_Password'] 
        dbn_dr = fd['DBName_Registry']
        dbn_measure = fd['DBName_Measurement']
        tbl_specific = fd['TblName_SpecificMetadata']
        tbl_dl = fd['TblName_DeviceList']

    print(server_ip)
    dbm = mqtt_DBManager.DBManager(db_host, db_user, db_pw, dbn_dr, dbn_measure, tbl_specific, tbl_dl)
    dbm.DB_Con()

    sensor_collector = mqtt_SensorCollector.SensorCollector(dbm, server_ip, port_sensor, mqtt_broker_host)
    #actuator_collector = mqtt_ActuatorCollector.ActuatorCollector(dbm, server_ip, port_actuator, mqtt_broker_host)
    
    sensor_collector.start()
    #actuator_collector.start()

    #actuator_collector.join()
    sensor_collector.join()  # 수정 : join()? 확인
    # join() : 해당 스레드가 종료되기까지 기다렸다가 다음으로 넘어감(스레드는 메인이 종료되어도 백그라운드에서 돌아감)