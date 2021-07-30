import threading
import time
import mqtt_DBManager
import paho.mqtt.client as mqtt

BUFFSIZE = 4096

# ConnectionRefusedError: [WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다.
# 해결방안? 서버-클라이언트 통신 시험용으로 idel 사용 시, 서버와 클라이언트 프로그램을 각각의 idel.exe에서 실행할 것

class ActuatorCollector(threading.Thread):
    def __init__(self, dbmanager = mqtt_DBManager.DBManager(), server_host='localhost', actuator_manager_port=11202, mqtt_broker_host='203.234.62.117'):
        threading.Thread.__init__(self)

        self.dbm = dbmanager
        self.system_id = "device0000"
        self.mqtt_broker_host = mqtt_broker_host

        self.PORT = actuator_manager_port 

    # MQTT function
    def on_connect(self, client, userdata, flags, rc):
        # 연결이 성공적으로 된다면 완료 메세지 출력
        if rc == 0:
            print("completely connected")
        else:
            print("Bad connection Returned code=", rc)
    
    # 연결이 끊기면 출력
    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))
    
    def on_publish(self, client, userdata, mid):
        print("In on_pub callback mid= ", mid)

    def run(self):
        print('AC >> run Actuator Collector')

        # 새로운 클라이언트 생성
        client = mqtt.Client()
        # 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_publish(메세지 발행)
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_publish = self.on_publish

        while True:
            print('AC >> Actuator Manager waiting...')
            
            # 로컬 아닌, 원격 mqtt broker에 연결
            # address : broker.hivemq.com
            # port: 1883 에 연결
            # 라즈베리파이 자신에게 MQTT 브로커가 설치되어 있으므로 자신의 IP를 넣어줌
            client.connect(self.mqtt_broker_host, 1883)
            client.loop_start()
            # 'test/hello' 라는 topic 으로 메세지 발행
            client.publish('test/sensor', send_data, 1)
            client.loop_stop()
            # 연결 종료
            client.disconnect()


    def thread(self, client_socket, addr):
        receive_id = "device0000"
        receive_id = self.receive(client_socket)
        #print("AC >> ", receive_id)

        table_name, item_id = self.dbm.get_item_list(receive_id)
        #print("AC >> table name : ", table_name, ", item id : ", item_id)

        if table_name != None and item_id != None:
            # self.send(client_socket, 'reg')
            print('AC >> Device is registered.')
        else:
            self.send(client_socket, 'notreg') # notreg : The device is not registered in DB
            print('AC >> cannot find the table : ', receive_id)
            return

        num = self.dbm.get_information_cnt(table_name)
        num2 = self.dbm.get_data_cnt(table_name)
        print("table num : ", num, " | event num : ", num2)

        if (num==1 and num2>0):
            # self.send(client_socket, '')
            
            actlist = []
            actlist = self.dbm.get_distinct_actlist(table_name)

            for i in actlist:
                rs = self.dbm.get_keyValue_act(i, table_name)

                if rs is not None:
                    actuator=rs[0]
                    status=rs[1]
                    msg = actuator + ":" + status
                    self.send(client_socket, msg)
                    # print("AC >> ", msg)

                self.dbm.delete_actuator_data(i, table_name)
        else:
            self.send(client_socket, 'noevt') # noevt : there is no event of the actutator

                