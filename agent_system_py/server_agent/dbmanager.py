try:
    import pymysql
except ImportError:
    print('not pymysql')

class DBManager():
    def __init__(self, port=11000, DB_h='localhost',DB_u='dsem_iot',DB_p='dsem_iot',DR_DB_NAME='DeviceRegistry',Sensor_DB_name="DeviceMeasurement",DB_s='specific_metadata',DB_r='device_register'):
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
                Tcp.SendStr('no')
                print('조회가 되질 않습니다')
        except Exception as e :
            Tcp.SendStr('no')
            print('error :', e)
        return table_name, item_id

    def get_sensor_actuator_list(self, item_id):
        num=self.curs.execute("SELECT metadata_value FROM "+self.DeviceRegistry_DB_name+'.'+self.Specific_table_name+ \
                            " WHERE item_id = "+self.addsq(item_id)+" AND (metadata_key like "+self.addsq('sensor-%') + \
                            " OR metadata_key like " + self.addsq('actuator-%') +");") # 특정 table의 칼럼값을 가져옴
        DB_column=self.curs.fetchall()
        return DB_column

    def insert_data(self, key, value):
        DB_sql='INSERT INTO '+ self.Sensor_DB_name+'.'+self.table_name+' ( timestamp,'
        
        #이부분 수정해야 함
        # key, value 리스트에 있는 것들을 모두 insert sql로 만들어서 execute 시킴
        
        # for i in DB_column:
        #     for j in i:
        #         DB_sql = DB_sql+j+','
        # DB_sql= DB_sql[:len(DB_sql)-1]+') VALUES ('
        # a= self.package_V(input_data[0])
        # input_data=input_data[1:]
        # data_list=[]
        # for i in input_data:
        #     data_list.append(i.split(':'))
        # data_dict = dict(data_list)
        # input_data=[]
        # for i in DB_column:
        #     for j in i:
        #         if j in data_dict:
        #             input_data.append(data_dict[j])
        #         else:
        #             input_data.append('NULL')
        # input_data.insert(0,(a))
        # s=",".join(input_data)
        # DB_sql= DB_sql+s+');'
        # self.curs.execute(DB_sql)
        # self.conn.commit()