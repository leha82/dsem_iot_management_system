import threading
import DBManager
import SensorCollector
import paho.mqtt.client as mqtt
import time

BUFFSIZE = 4096

class ActuatorController(threading.Thread):
    # def __init__(self, dbmanager = DBManager.DBManager(), server_host='localhost', actuator_manager_port=11202, mqtt_broker_ip='203.234.62.117'):
    def __init__(self, dbmanager = DBManager.DBManager(), mqtt_broker_ip=''):
        threading.Thread.__init__(self)

        self.dbm = dbmanager
        # self.system_id = "device0004"
        self.broker_ip = mqtt_broker_ip

        # self.PORT = actuator_manager_port 

    # MQTT function
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("completely connected")
        else:
            print("Bad connection Returned code=", rc)
    
    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))
    
    def on_publish(self, client, userdata, mid):
        print("In on_pub callback mid= ", mid)

    def run(self):
        print('AC >> run Actuator Collector')

        # New Client Create
        client = mqtt.Client()
        # Callback function settings... on_connect(Connection to Broker), on_disconnect(Disconnect to Broker), on_publish
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_publish = self.on_publish

        print('AC >> Actuator Manager waiting...')
        system_id=""
        table_name, item_id = self.dbm.get_item_list(system_id)

        num = self.dbm.get_information_cnt(table_name)
        num2 = self.dbm.get_data_cnt(table_name)
        print("table num : ", num, " | event num : ", num2)

        if (num==1 and num2>0):
            actlist = []
            actlist = self.dbm.get_distinct_actlist(table_name)

            for i in actlist:
                rs = self.dbm.get_keyValue_act(i, table_name)

                if rs is not None:
                    actuator=rs[0]
                    status=rs[1]
                    msg = actuator + ":" + status
                    print(msg)
                    
                    client.connect(self.broker_ip, 1883)
                    client.loop_start()
                    client.publish('data/actuator', msg, 1)
                    client.loop_stop()
                    client.disconnect()

                self.dbm.delete_actuator_data(i, table_name)

        time.sleep(5)
            