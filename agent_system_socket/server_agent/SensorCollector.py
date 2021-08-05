import threading
import socket
import DBManager
import json

BUFFSIZE = 4096

frontstr = "SC >> "

class SensorCollector (threading.Thread):
    def __init__(self, dbmanager = DBManager.DBManager(), server_host='localhost', sensor_manager_port=11201):
        threading.Thread.__init__(self)

        self.dbm = dbmanager
        if server_host == 'localhost':
            self.HOST = socket.gethostbyname(socket.getfqdn()) # automatically assign ip address as server's own ip address
            print(frontstr, "set HOST: ", self.HOST)
        else:
            self.HOST = server_host
            print(frontstr, "set HOST: ", self.HOST)
        self.PORT = sensor_manager_port 

    def run(self):
        print(frontstr, "run Sensor Collector")
        server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket1.bind((self.HOST, self.PORT))
        server_socket1.listen()

        try:
            while True:
                print(frontstr, "Sensor Manager waiting...")

                client_socket, addr = server_socket1.accept()
                print(frontstr, "Connected by ", addr)

                sensor_thread = threading.Thread(target=self.thread, args=(client_socket, addr,))
                sensor_thread.start()  
                
        except KeyboardInterrupt:
            print(frontstr, "Keyboard Interrupt. Program is Terminated")

    def send(self, client_socket, message):
        client_socket.send(bytes(message,"UTF-8"))
        print(frontstr, "send : ", message)

    def receive(self, client_socket):
        recv_msg = client_socket.recv(BUFFSIZE).decode("UTF-8")
        print(frontstr, "receive : ", recv_msg)
        return recv_msg

    def thread(self, client_socket, addr):
        try:
            # system_id = self.receive(client_socket)
            # print(frontstr, system_id)

            receive_data = self.receive(client_socket)
            
            if receive_data != "":
                receive_data = receive_data.replace("'", "\"")
                jsondata = json.loads(receive_data)
                #print(type(jsondata))

                system_id = jsondata["system_id"]

                table_name, item_id = self.dbm.get_item_list(system_id)
                print(frontstr, "table name : ", table_name, ", item id : ", item_id)

                if table_name == None or item_id == None:
                    self.send(client_socket, "notreg")
                    print(frontstr, "Cannot find the system_id : ", system_id)
                else:
                    print(frontstr, "Connected : ", system_id, " [item id : ", item_id, "]")

                    del jsondata["system_id"]
                    print(frontstr, "receive_data:", jsondata)

                    # make key list and value list from received json data
                    key_list = []
                    value_list = []
                    for key, value in jsondata.items():
                        key_list.append(key)
                        value_list.append(value)

                    # get sensor and actuator list from specific metadata table in database
                    DB_column = []
                    DB_column=self.dbm.get_sensor_actuator_list(item_id)
                    print(frontstr, "DB_column : " , DB_column)

                    # make DB_column_list from select query result DB_Column.
                    DB_column_list = []
                    for i in range(len(DB_column)):
                        DB_column_list.append(DB_column[i][0])  # DB_column has format like (('humidity',), ('temperature', ), ...) 
                    print(frontstr, "DB_column_list : ", DB_column_list)

                    # make (key,value) list that only the key is included in db_column list
                    input_list = []
                    for i in range(len(key_list)):
                        if key_list[i] in DB_column_list:
                            input_list.append([key_list[i], str(value_list[i])])
                    print(frontstr, "input_list : ", input_list)

                    # insert the (key, value) list to device measurement db
                    self.dbm.insert_data(input_list, table_name)
                    self.send(client_socket, "accept")

            client_socket.close()
            
        except Exception as e :
            print(frontstr, "error > ", e)
            
            return
                
