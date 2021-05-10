import json

if __name__ == "__main__":
    server = TcpServer.TcpServer()
    file_path = './config.json'
    with open(file_path, "r") as fj:
        fd = json.load(fj)
        a = fd['PORT']
        b = fd['DB_Host']
        c = fd['DB_User']
        d = fd['DB_password'] 
        e = fd['DeviceRegistry_DB_name']
        f = fd['Sensor_DB_name']
        g = fd['Specific_table_name']
        h = fd['Device_Register_table_name']
    dbm = DBManager(b,c,d,e,f,g,h)
    dbm.DB_Con()
    server=TcpServer.TcpServer(dbm, a)
    while True:
        # server.runSensorManager()
        # server.runActuatorManager()

        sensor_thread = threading.Thread(target=server.sensorThread, args=())
        actuator_thread = threading.Thread(target=server.actuatorThread, args=())
