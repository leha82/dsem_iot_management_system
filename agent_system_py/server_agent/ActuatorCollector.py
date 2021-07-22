import threading
import socket
import time
import DBManager

BUFFSIZE = 4096

# ConnectionRefusedError: [WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다.
# 해결방안? 서버-클라이언트 통신 시험용으로 idel 사용 시, 서버와 클라이언트 프로그램을 각각의 idel.exe에서 실행할 것

class ActuatorCollector(threading.Thread):
    def __init__(self, dbmanager = DBManager.DBManager(), server_host='localhost', actuator_manager_port=11202):
        threading.Thread.__init__(self)

        self.dbm = dbmanager
        if server_host == 'localhost':
            self.HOST = socket.gethostbyname(socket.getfqdn()) # 서버 ip주소 자신의 아이피로 자동 할당
            print("set HOST:"+self.HOST)
        else:
            self.HOST = server_host
            print(self.HOST)
        self.PORT = actuator_manager_port 

    def run(self):
        print('AC >> run Actuator Collector')
        server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 수정 : SOL_SOCKET, SO_REuSEADDR 확인
        # 이미 사용된 주소를 재사용(bind) 하도록 한다.
        server_socket2.bind((self.HOST, self.PORT))
        server_socket2.listen()

        try:
            while True:
                print('AC >> Actuator Manager waiting...')

                client_socket, addr = server_socket2.accept()
                print('AC >> Connected by', addr)

                actuator_thread = threading.Thread(target=self.thread, args=(client_socket, addr,))
                actuator_thread.start() 
                
        except KeyboardInterrupt:
            print('AC >> Actuator Collector is stopped.')

    def send(self, client_socket, message):
        client_socket.send(bytes(message,"UTF-8"))
        print("AC >> send : ", message)

    def receive(self, client_socket):
        recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8")
        print("AC >> receive : ", recv_msg)
        return recv_msg

    def thread(self, client_socket, addr):
        receive_id = self.receive(client_socket)
        print("AC >> ", receive_id)

        table_name, item_id = self.dbm.get_item_list(receive_id)
        print("AC >> table name : ", table_name, ", item id : ", item_id)

        if table_name != None and item_id != None:
            # self.send(client_socket, 'reg')
            print('AC >> Device is registered.')
        else:
            self.send(client_socket, 'notreg') # notreg : The device is not registered in DB
            print('AC >> cannot find the table : ', receive_id)
            return

        num = self.dbm.get_information_cnt(table_name)
        num2 = self.dbm.get_data_cnt(table_name)

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
                    # print("AA >> ", msg)

                self.dbm.delete_actuator_data(i, table_name)
        else:
            self.send(client_socket, 'noevt') # noevt : there is no event of the actutator
        client_socket.close()

                