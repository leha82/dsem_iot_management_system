import threading
import DBManager
import json
import socket
import paho.mqtt.client as mqtt

BUFFSIZE = 4096

class SensorCollector (threading.Thread):
    def __init__(self, dbmanager = DBManager.DBManager(), server_host='localhost', sensor_manager_port=11201, mqtt_broker_host='203.234.62.117'):
        threading.Thread.__init__(self)

        self.dbm = dbmanager
        self.system_id = "device0000"
        self.mqtt_broker_host = mqtt_broker_host

        self.PORT = sensor_manager_port # 포트 는 10000이상으로 쓰고 겹치지 않는지 확인하며 할당 할 것

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
            # 보내는 데이터가 humidity=50.0!temperature=20.1!... 이런식으로 올 수 있도록
            receive_data = receive_data.replace("'", "\"")
            jsondata = json.loads(receive_data)
            #print(type(jsondata))
    
            self.system_id = jsondata["system_id"]
            print(self.system_id)

            table_name, item_id = self.dbm.get_item_list(self.system_id)
            #print("table name : ", table_name, ", item id : ", item_id)

            del jsondata["system_id"]
            print("receive_data:", jsondata)

            # input_data를 key, value 리스트로 각각 분리해서 만들 수 있도록 해야함
            key_list = []
            value_list = []
            for key, value in jsondata.items():
                key_list.append(key)
                value_list.append(value)

            # Specific metadata에 저장된 sensor 및 actuator를 받아와 list up 시킴
            DB_column = []
            DB_column=self.dbm.get_sensor_actuator_list(item_id)
            #print("DB_column : " , DB_column)

            # DB_column의 리스트와 key 리스트를 비교하여 key 리스트의 값이 DB_column에 존재하지 않으면 해당 key는 db로 넣지 못함
            DB_column_list = []
            for i in range(len(DB_column)):
                DB_column_list.append(DB_column[i][0])  # (('humidity',), ('temperature', ), ...) 이런식으로 되어 있음
            #print("DB_column_list : ", DB_column_list)

            input_list = []
            for i in range(len(key_list)):
                if key_list[i] in DB_column_list:   # in, not in : Java의 append함수
                    input_list.append([key_list[i], str(value_list[i])])
            #print("input_list : ", input_list)

            # key, value 리스트를 dbm의 insert_data로 넣도록 함
            self.dbm.insert_data(input_list, table_name)


    def run(self):
        print('run Sensor Collector')

        while True:
            # 새로운 클라이언트 생성
            client = mqtt.Client()
            # 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_subscribe(topic 구독),
            # on_message(발행된 메세지가 들어왔을 때)
            client.on_connect = self.on_connect
            client.on_disconnect = self.on_disconnect
            client.on_subscribe = self.on_subscribe
            client.on_message = self.on_message

            client.connect(self.mqtt_broker_host, 1883)
            client.subscribe('data/sensor', 1)
            client.loop_forever()

            #client.disconnect()
            # client.loop_forever() 를 사용하는 경우, 메소드는 현재 스레드를 사용하여 클라이언트의 네트워크
            # 스레드를 실행하고 해당 호출에서 해당 블록을 실행
            # client.loop_start() 를 사용하는 경우 그런 다음 백그라운드에서 새 스레드를 시작하여 네트워크 루프
            # 와 모든 콜백을 실행