import threading
import socket
import DBManager
import json

BUFFSIZE = 4096

class SensorCollector (threading.Thread):
    def __init__(self, dbmanager = DBManager.DBManager(), server_host='localhost', sensor_manager_port=11201):
        threading.Thread.__init__(self)

        self.dbm = dbmanager
        if server_host == 'localhost':
            self.HOST = socket.gethostbyname(socket.getfqdn()) # 서버 ip주소 자신의 아이피로 자동 할당
            print("set HOST:"+self.HOST)
        else:
            self.HOST = server_host
            print(self.HOST)
        self.PORT = sensor_manager_port # 포트 는 10000이상으로 쓰고 겹치지 않는지 확인하며 할당 할 것

    def run(self):
        print('run Sensor Collector')
        server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket1.bind((self.HOST, self.PORT))
        server_socket1.listen()

        try:
            while True:
                print('Sensor Manager waiting...')

                client_socket, addr = server_socket1.accept()
                print('Connected by', addr)

                sensor_thread = threading.Thread(target=self.thread, args=(client_socket, addr,))
                sensor_thread.start()  # 수정 : start() 실험
                # run()은 병행 처리를 못함 -> 이전의 스레드가 종료되어야 다른 스레드 실행됨
                # start()는 병행 처리 가능 (start를 사용해야함)
                
        except KeyboardInterrupt:
            print('동작을 중지하였습니다.')

    def send(self, client_socket, message):
        client_socket.send(bytes(message,"UTF-8"))
        print("sensor collector send : ", message)

    def receive(self, client_socket):
        recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8")
        print("sensor collector receive : ", recv_msg)
        return recv_msg

    def thread(self, client_socket, addr):
        try:
            system_id = self.receive(client_socket)
            #print(receive_id)

            table_name, item_id = self.dbm.get_item_list(system_id)
            #print("table name : ", table_name, ", item id : ", item_id)

            if table_name != None and item_id != None:
                self.send(client_socket, 'yes')
                print('Connected : ', system_id, ' [item id : ',item_id,']')
            else:
                self.send(client_socket, 'no')
                print('조회가 되질 않습니다')
                return
            
            receive_data = self.receive(client_socket)

            if receive_data != "":
                # 보내는 데이터가 humidity=50.0!temperature=20.1!... 이런식으로 올 수 있도록
                receive_data = receive_data.replace("'", "\"")
                jsondata = json.loads(receive_data)
                #print(type(jsondata))

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
                # 수정 : 91~101 코드 정리
                DB_column_list = []
                for i in range(len(DB_column)):
                    DB_column_list.append(DB_column[i][0])  # (('humidity',), ('temperature', ), ...) 이런식으로 되어 있음
                #print("DB_column_list : ", DB_column_list)

                input_list = []
                for i in range(len(key_list)):
                    if key_list[i] in DB_column_list:   # in, not in : Java의 append함수
                        input_list.append([key_list[i], str(value_list[i])])
                print("input_list : ", input_list)

                # key, value 리스트를 dbm의 insert_data로 넣도록 함
                self.dbm.insert_data(input_list, table_name)
                client_socket.close()
            
        except Exception as e :
            self.send(client_socket, 'no')
            print('error :', e)
            return
                