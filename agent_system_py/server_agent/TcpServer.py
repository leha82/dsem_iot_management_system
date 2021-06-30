
import TcpNet
import threading
import dbmanager

# try:
#     import pymysql
# except ImportError:
#     print('not pymysql')

class TcpServer:
    def __init__(self, dbmanager = dbmanager.dbmanager(), server_host='localhost', sensor_manager_port=11201, actuator_manager_port=11202):
        self.dbm = dbmanager
        
        if server_host == 'localhost':
            self.tcp = TcpNet.TcpNet()
            self.HOST = TcpNet.ipcheck() # 서버 ip주소 자신의 아이피로 자동 할당
            print("set HOST:"+self.HOST)
        else:
            self.HOST = server_host
            print(self.HOST)
        self.SM_PORT = sensor_manager_port # 포트 는 10000이상으로 쓰고 겹치지 않는지 확인하며 할당 할 것
        self.AM_PORT = actuator_manager_port # 포트 는 10000이상으로 쓰고 겹치지 않는지 확인하며 할당 할 것
  
    def package_V(self,s): # 문자열 쌓아주는 함수
        return '\''+str(s)+'\''

    def runSensorManager(self):
        tcp = TcpNet.TcpNet()
        print('Sensor Manamger waiting...')
        tcp.Accept(IP=self.HOST,Port=self.SM_PORT)
        sensor_thread = threading.Thread(target=self.sensorThread, args=(tcp,))

    def runActuatorManager(self):
        tcp = TcpNet.TcpNet()
        print('Actuator Manager waiting...')
        tcp.Accept(IP=self.HOST,Port=self.AM_PORT)
        actuator_thread = threading.Thread(target=self.actuatorThread, args=(tcp,))


    def sensorThread(self):
        Tcp = TcpNet.TcpNet()
        print('Sensor Manager waiting...')
        Tcp.Accept(IP=self.HOST,Port=self.SM_PORT)

        try:
            receive_id=Tcp.ReceiveStr()
            table_name, item_id = self.dbm.get_item_list(receive_id)

            if table_name != None and item_id != None:
                Tcp.SendStr('yes')
                print('Connected : ', receive_id, ' [item id : ',item_id,']')
            else:
                Tcp.SendStr('no')
                print('조회가 되질 않습니다')
                return
        except Exception as e :
            Tcp.SendStr('no')
            print('error :', e)
            return

        receive_data=Tcp.ReceiveStr()
        
        if receive_data != "":
            # 보내는 데이터가 humidity=50.0!temperature=20.1!... 이런식으로 올 수 있도록
            print("receive_data:"+receive_data)
            input_data=receive_data.split('!')
            # input_data를 key, value 리스트로 각각 분리해서 만들 수 있도록 해야함
            key_value_list = []
            for i in range(1, len(input_data)):
                key_value_list=input_data[i].split(':')

            # Specific metadata에 저장된 sensor 및 actuator를 받아와 list up 시킴
            DB_column=self.dbm.get_sensor_actuator_list(item_id)

            # DB_column의 리스트와 key 리스트를 비교하여 key 리스트의 값이 DB_column에 존재하지 않으면 해당 key는 db로 넣지 못함
            DB_column_list = []
            for i in range(len(DB_column)):
                DB_column_list = DB_column[i][0]

            input_list = []
            for i in range(len(key_value_list)):
                for j in range(len(DB_column_list)):
                    if (DB_column_list[j] == key_value_list[i][0]):
                        input_list.append(key_value_list[i])
                    break
            # key, value 리스트를 dbm의 insert_data로 넣도록 함
            self.dbm.insert_data(input_list)

    # 새로운 스레드
    def actuatorThread(self):
        Tcp = TcpNet.TcpNet()
        print('Actuator Manager waiting...')
        Tcp.Accept(IP=self.HOST,Port=self.AM_PORT)

        self.curs.execute("SELECT count(*) FROM Information_schema.tables WHERE table_schema='" + self.Sensor_DB_name + "' AND table_name='" + self.table_name + "_act';")
        rs = self.curs.fetchone()
        num2=rs[0]
        
        cnt=self.curs.execute("SELECT COUNT(*) FROM " + self.Sensor_DB_name + "." + self.table_name + "_act;")
        rs = self.curs.fetchone()
        cnt=rs[0]
        
        if(num2 == 1 and cnt > 0 ):
            Tcp.SendStr('yesAct')
            self.curs.execute("SELECT DISTINCT actuator FROM " + self.Sensor_DB_name + "." + self.table_name + "_act;")
            act2 = self.curs.fetchall()
            newlist = [data[0] for data in act2]
            
            for i in newlist:
                self.curs.execute("SELECT actuator, status FROM " + self.Sensor_DB_name + "." + self.table_name + "_act WHERE actuator='" + i + "' order by timestamp desc limit 1;")
                rs = self.curs.fetchone()
                if rs is not None:
                    actuator=rs[0]
                    status=rs[1]
                    msg=actuator + ":" + status
                    Tcp.SendStr(msg)
                    #print(msg)
                
                delete_sql = "DELETE FROM " + self.Sensor_DB_name + "." + self.table_name + "_act WHERE actuator='" + i + "';"
                self.curs.execute(delete_sql)
                self.conn.commit()
        else:
            Tcp.SendStr('noAct')