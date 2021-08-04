try:
    import pymysql
except ImportError:
    print('not pymysql')

class DBManager:
    def __init__(self, DB_h='203.234.62.115', DB_p=3306, DB_u='dsem_iot',DB_pw='dsem_iot',DR_DB_NAME='DeviceRegistry',Sensor_DB_name="DeviceMeasurement",DB_s='specific_metadata',DB_r='device_register'):
        self.DB_Host= DB_h # DB 주소
        self.DB_Port= DB_p
        self.DB_User= DB_u # 접속할 아이디 
        self.DB_password = DB_pw # 접속할 아이디의 비밀번호
        self.DR_DB_NAME = DR_DB_NAME # 디바이스레지스트리 DB의 이름
        self.Sensor_DB_name=Sensor_DB_name # Sensor DB 이름
        self.Specific_table_name = DB_s # specific_metadata테이블 이름
        self.DR_TBL_NAME = DB_r # 디바이스 리스트들은 테이블 이름
        self.charset = 'utf8' # 형식

    def DB_Con(self):
        self.conn = pymysql.connect(host=self.DB_Host,port=self.DB_Port, user=self.DB_User, password=self.DB_password,db=self.DR_DB_NAME, charset=self.charset) # DB연결 나중에 예외처리 해줄것
        self.curs = self.conn.cursor() # DB 커서
        print('DB connected.....')

    # 문자열 쌓아주는 함수
    def addsq(self,s): 
        return '\''+str(s)+'\''

    def get_item_list(self, receive_id):
        try:
            sql = "SELECT system_id,table_name, item_id FROM "+self.DR_DB_NAME+"."+self.DR_TBL_NAME + \
                            " WHERE system_id = " +self.addsq(receive_id)+";"
            print("dbm >> ", sql)
            self.curs.execute(sql)
            result = self.curs.fetchone()
            if(result[0] is not None):
                table_name=result[1]
                item_id=result[2]
            else:
                return None, None
        except Exception as e :
            return None, None
        # print(table_name, item_id)
        return table_name, item_id

    def get_sensor_actuator_list(self, item_id):
        sql = "SELECT metadata_value FROM "+self.DR_DB_NAME+'.'+self.Specific_table_name+ \
                            " WHERE item_id = "+self.addsq(item_id)+" AND (metadata_key like "+self.addsq('sensor-%') + \
                            " OR metadata_key like " + self.addsq('actuator-%') +");"
        print("dbm >> ", sql)
        num=self.curs.execute(sql) # 특정 table의 칼럼값을 가져옴
        DB_column=self.curs.fetchall()
        return DB_column

    # 해당 table이 존재하는지 아닌지를 0 또는 1로 표현
    def get_information_cnt(self, table_name):
        sql = "SELECT count(*) FROM Information_schema.tables WHERE table_schema='"+self.Sensor_DB_name+\
                            "' AND table_name='"+table_name+"_act';"
        print("dbm >> ", sql)
        self.curs.execute(sql)
        rs = self.curs.fetchone()
        num = rs[0]
        return num

    # 해당 table 내에 데이터 row가 존재하는지 아닌지 
    def get_data_cnt(self, table_name):
        sql = "SELECT count(*) FROM "+self.Sensor_DB_name+"."+table_name+"_act;"
        print("dbm >> ", sql)
        self.curs.execute(sql)
        rs = self.curs.fetchone()
        num = rs[0]
        print("dbm >> ", num)
        
        self.conn.commit()

        return num

    # Actuator 제어 요청(중복 없이) 가져오기
    def get_distinct_actlist(self, table_name):
        sql = "SELECT DISTINCT actuator FROM "+self.Sensor_DB_name+"."+table_name+"_act;"
        print("dbm >> ", sql)
        self.curs.execute(sql)
        act = self.curs.fetchall()
        newlist = [data[0] for data in act]
        return newlist

    # key:value 형태로 actuator 데이터 가져오기
    def get_keyValue_act(self, i, table_name):
        sql = "SELECT actuator, status FROM "+self.Sensor_DB_name+"."+table_name+"_act WHERE actuator='"+i+\
                                "' order by timestamp desc limit 1;"
        print("dbm >> ", sql)
        self.curs.execute(sql)
        rs = self.curs.fetchone()
        return rs

    # 사용한 actuator 데이터 삭제
    def delete_actuator_data(self, i, table_name):
        sql = "DELETE FROM " + self.Sensor_DB_name + "." + table_name + "_act WHERE actuator='" + i + "';"
        print("dbm >> ", sql)
        self.curs.execute(sql)
        self.conn.commit()

    # 데이터 insert 함수
    def insert_data(self, input_list, table_name):
        DB_sql='INSERT INTO '+ self.Sensor_DB_name+'.'+ table_name +' ( timestamp, '
        # key
        for i in range(len(input_list)):
            key = input_list[i][0]
            if i == len(input_list) - 1:
                DB_sql = DB_sql + key
            else:
                DB_sql = DB_sql + key +', '
        DB_sql= DB_sql[:len(DB_sql)]+') VALUES (now(), ' 
        # value
        for i in range(len(input_list)):
            value = input_list[i][1]
            if i == len(input_list)-1:
                DB_sql = DB_sql +"'"+value + "'"
            else:
                DB_sql = DB_sql + "'"+value + "',"
        DB_sql= DB_sql+');'
        print(DB_sql)
        self.curs.execute(DB_sql)
        self.conn.commit()
