
import TcpNet
import threading

# try:
#     import pymysql
# except ImportError:
#     print('not pymysql')

class TcpServer():
    def __init__(self, dbmanager = DBManager(), server_host='localhost', sensor_manager_port=11201, actuator_manager_port=11202):
        self.dbm = dbmanager
        
        if server_host == 'localhost':
            self.HOST = TcpNet.GetHostIP() # 서버 ip주소 자신의 아이피로 자동 할당
            print("set HOST:"+self.HOST)
        else:
            self.HOST = server_host

        self.SM_PORT = sensor_manager_port # 포트 는 10000이상으로 쓰고 겹치지 않는지 확인하며 할당 할 것
        self.AM_PORT = actuator_manager_port # 포트 는 10000이상으로 쓰고 겹치지 않는지 확인하며 할당 할 것
  
    def package_V(self,s): # 문자열 쌓아주는 함수
        return '\''+str(s)+'\''

    def runSensorManager(self):
        tcp = TcpNet.TcpNet()
        print('Sensor Manamger waiting...')
        tcp.Accept(IP=self.HOST,Port=self.SM_PORT)
        sensor_thread = threading.Thread(target=sensorThread, args=(tcp,))

    def runActuatorManager(self):
        tcp = TcpNet.TcpNet()
        print('Actuator Manager waiting...')
        tcp.Accept(IP=self.HOST,Port=self.AM_PORT)
        actuator_thread = threading.Thread(target=actuatorThread, args=(tcp,))


    def sensorThread(self):
        Tcp = TcpNet.TcpNet()
        print('Sensor Manamger waiting...')
        Tcp.Accept(IP=self.HOST,Port=self.SM_PORT)

        try:
            receive_id=Tcp.ReceiveStr()
            table_name, item_id = dbm.get_item_list(receive_id)

            if table_name != null and item_id != null:
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

            # Specific metadata에 저장된 sensor 및 actuator를 받아와 list up 시킴
            DB_column=dbm.get_sensor_actuator_list(item_id)

            # DB_column의 리스트와 key 리스트를 비교하여 key 리스트의 값이 DB_column에 존재하지 않으면 해당 key는 db로 넣지 못함

            # key, value 리스트를 dbm의 insert_data로 넣도록 함
            dbm.insert_data(key, value)



#여기서부터는 지울 것
        while True:
            ack = Tcp.ReceiveStr()
            if(ack=='send'):
                Tcp.SendStr('con')
            receive_data=Tcp.ReceiveStr()
            if receive_data != "":
                print("receive_data:"+receive_data)
                input_data=receive_data.split('!')
                DB_column=dbm.get_sensor_actuator_list(item_id)

                DB_sql='INSERT INTO '+ self.Sensor_DB_name+'.'+self.table_name+' ( timestamp,'
                for i in DB_column:
                    for j in i:
                        DB_sql = DB_sql+j+','
                DB_sql= DB_sql[:len(DB_sql)-1]+') VALUES ('
                a= self.package_V(input_data[0])
                input_data=input_data[1:]
                data_list=[]
                for i in input_data:
                    data_list.append(i.split(':'))
                data_dict = dict(data_list)
                input_data=[]
                for i in DB_column:
                    for j in i:
                        if j in data_dict:
                            input_data.append(data_dict[j])
                        else:
                            input_data.append('NULL')
                input_data.insert(0,(a))
                s=",".join(input_data)
                DB_sql= DB_sql+s+');'
                self.curs.execute(DB_sql)
                self.conn.commit()
                ack=None

            # Actuator data
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
            else:
                print(receive_id, ' Disconnected............')
                break
                
            if receive_data =='exit':
                print('socket end')
                break




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