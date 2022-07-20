import threading
import DBManager
import json
import paho.mqtt.client as mqtt

BUFFSIZE = 4096

class SensorCollector (threading.Thread):
    def __init__(self, dbmanager = DBManager.DBManager(), mqtt_broker_host=''):
        threading.Thread.__init__(self)
        self.dbm = dbmanager
        self.mqtt_broker_host = mqtt_broker_host

    # MQTT function
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, client, userdata, msg):
        receive_data = str(msg.payload.decode("utf-8"))
        print("received message = ", receive_data)

        if receive_data != "":
            receive_data = receive_data.replace("'", "\"")
            jsondata = json.loads(receive_data)
            #print(type(jsondata))
    
            system_id = jsondata["system_id"]
            print(system_id)

            table_name, item_id = self.dbm.get_item_list(system_id)
            #print("table name : ", table_name, ", item id : ", item_id)

            # make key list and value list from received json data
            key_list = []
            value_list = []
            temp_object=jsondata['content']
            for key in temp_object:
                key_list.append(key)
                value_list.append(temp_object.get(key))
                #print("{}, {}".format(key,temp_object.get(key)))

            # get sensor and actuator list from specific metadata table in database
            DB_column = []
            DB_column = self.dbm.get_sensor_actuator_list(item_id)
            #print("DB_column : " , DB_column)

            # make DB_column_list from select query result DB_Column.
            DB_column_list = []
            for i in range(len(DB_column)):
                DB_column_list.append(DB_column[i][0])  # DB_column has format like (('humidity',), ('temperature', ), ...) 
            #print("DB_column_list : ", DB_column_list)

            # make (key,value) list that only the key is included in db_column list
            input_list = []
            for i in range(len(key_list)):
                if key_list[i] in DB_column_list:  
                    input_list.append([key_list[i], str(value_list[i])])
            #print("input_list : ", input_list)

            # insert the (key, value) list to device measurement db
            self.dbm.insert_data(input_list, table_name)


    def run(self):
        print('run Sensor Collector')

        while True:
            # make mqtt client
            client = mqtt.Client()
            # set callback function : on_connect(), on_disconnect()
            # on_subscribe() : callback after accept the subscribe from broker
            # on_message() : callback after the broker send message.
            client.on_connect = self.on_connect
            client.on_disconnect = self.on_disconnect
            client.on_subscribe = self.on_subscribe
            client.on_message = self.on_message

            client.connect(self.mqtt_broker_host, 1883)
            client.subscribe('+/DATA', 1)
            client.loop_forever()

            client.disconnect()
