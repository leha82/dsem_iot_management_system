import threading
import socket
import time
import DBManager

BUFFSIZE = 4096

class ActuatorController(threading.Thread):
    def __init__(self, dbmanager = DBManager.DBManager(), server_host='localhost', actuator_manager_port=11202):
        threading.Thread.__init__(self)

        self.dbm = dbmanager
        if server_host == 'localhost':
            self.HOST = socket.gethostbyname(socket.getfqdn()) # automatically assign ip address as server's own ip address
            print("set HOST:"+self.HOST)
        else:
            self.HOST = server_host
            print(self.HOST)
        self.PORT = actuator_manager_port 

    def run(self):
        print('AC >> run Actuator Collector')
        server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
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
        client_socket.close()

                
