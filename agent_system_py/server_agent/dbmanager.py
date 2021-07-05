try:
    import pymysql
except ImportError:
    print('not pymysql')

class DBManager:
    def __init__(self, DB_h='203.234.62.115',DB_u='dsem_iot',DB_p='dsem_iot',DR_DB_NAME='DeviceRegistry',Sensor_DB_name="DeviceMeasurement",DB_s='specific_metadata',DB_r='device_register'):
        # self.HOST= TcpNet.ipcheck(); # 서버 ip주소 자신의 아이피로 자동 할당
        # print("set HOST:"+self.HOST)
        # self.PORT= port # 포트 는 10000이상으로 쓰고 겹치지 않는지 확인하며 할당 할 것
        self.DB_Host= DB_h # DB 주소
        self.DB_User= DB_u # 접속할 아이디 
        self.DB_password = DB_p # 접속할 아이디의 비밀번호
        self.DR_DB_NAME = DR_DB_NAME # 디바이스레지스트리 DB의 이름
        self.Sensor_DB_name=Sensor_DB_name # Sensor DB 이름
        self.Specific_table_name = DB_s # specific_metadata테이블 이름
        self.DR_TBL_NAME = DB_r # 디바이스 리스트들은 테이블 이름
        self.charset = 'utf8' # 형식
        # self.table_name = '' #  데이터넣을 테이블 이름 변수 선언
        # self.item_id = ''

    def DB_Con(self):
        self.conn = pymysql.connect(host=self.DB_Host,user=self.DB_User, password=self.DB_password,db=self.DR_DB_NAME, charset=self.charset) # DB연결 나중에 예외처리 해줄것
        self.curs = self.conn.cursor() # DB 커서
        print('DB connected.....')

    def addsq(self,s): # 문자열 쌓아주는 함수
        return '\''+str(s)+'\''

    def get_item_list(self, receive_id):
        try:
            self.curs.execute("SELECT system_id,table_name, item_id FROM "+self.DR_DB_NAME+"."+self.DR_TBL_NAME + \
                            " WHERE system_id = " +self.addsq(receive_id)+";")
            result = self.curs.fetchone()
            if(result[0] is not None):
                table_name=result[1]
                item_id=result[2]
            else:
                return None, None
        except Exception as e :
            return None, None
        print(table_name, item_id)
        return table_name, item_id

    def get_sensor_actuator_list(self, item_id):
        num=self.curs.execute("SELECT metadata_value FROM "+self.DR_DB_NAME+'.'+self.Specific_table_name+ \
                            " WHERE item_id = "+self.addsq(item_id)+" AND (metadata_key like "+self.addsq('sensor-%') + \
                            " OR metadata_key like " + self.addsq('actuator-%') +");") # 특정 table의 칼럼값을 가져옴
        DB_column=self.curs.fetchall()
        return DB_column

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