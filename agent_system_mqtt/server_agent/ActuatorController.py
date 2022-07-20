import threading
import DBManager
import json
import paho.mqtt.client as mqtt

BUFFSIZE = 4096

class TestSesor (threading.Thread):
    def __init__(self, dbmanager = DBManager.DBManager(), mqtt_broker_host=''):
        threading.Thread.__init__(self)
        self.dbm = dbmanager
        self.mqtt_broker_host = mqtt_broker_host
        self.system_id = ""

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
            print(jsondata)


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
            client.subscribe('+/sensor', 1)
            client.loop_forever()

            client.disconnect()