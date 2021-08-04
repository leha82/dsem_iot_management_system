try:
    import pymysql
except ImportError:
    print('not pymysql')

class DBManager:
    def __init__(self, DB_host='', DB_port=3306, DB_userid='', DB_pw='', DBN_device_registry='DeviceRegistry', DBN_device_measurement="DeviceMeasurement", tbl_specific='specific_metadata', tbl_dl='device_list'):
        self.DB_host= DB_host # Database ip address
        self.DB_port= DB_port # Database port number
        self.DB_user= DB_userid # Database user id
        self.DB_password = DB_pw # database password
        self.DBN_dr = DBN_device_registry # database name for device registry
        self.DBN_dm=DBN_device_measurement # database name for device measurement
        self.tbl_specific = tbl_specific # table name for specific_metadata
        self.tbl_dl = tbl_dl # table name for device list
        self.charset = 'utf8'

    def DB_Con(self):
        self.conn = pymysql.connect(host=self.DB_host, port=self.DB_port, user=self.DB_user, password=self.DB_password,db=self.DBN_dr, charset=self.charset) # DB연결 나중에 예외처리 해줄것
        self.curs = self.conn.cursor()
        print('DB connected.....')

    # add single quotation mark at the string
    def addsq(self,s): 
        return '\''+str(s)+'\''

    # get a list of all items from device registry
    def get_item_list(self, receive_id):
        try:
            sql = "SELECT system_id, table_name, item_id FROM " + self.DBN_dr + "." + self.tbl_dl + \
                            " WHERE system_id = " + self.addsq(receive_id) + ";"
            #print("dbm >> ", sql)
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

    # get sensor list and actuator list from specific metadata table
    def get_sensor_actuator_list(self, item_id):
        sql = "SELECT metadata_value FROM " + self.DBN_dr + '.' + self.tbl_specific + \
                            " WHERE item_id = " + self.addsq(item_id) + " AND (metadata_key like " + self.addsq('sensor-%') + \
                            " OR metadata_key like " + self.addsq('actuator-%') +");"
        #print("dbm >> ", sql)
        num=self.curs.execute(sql) 
        DB_column=self.curs.fetchall()
        return DB_column

    # check the actuator event is exist. 
    # if the actuation is exist, return 1. if not, return 0.
    def get_information_cnt(self, table_name):
        sql = "SELECT count(*) FROM Information_schema.tables WHERE table_schema='" + self.DBN_dm + \
                            "' AND table_name='" + table_name + "_act';"
        #print("dbm >> ", sql)
        self.curs.execute(sql)
        rs = self.curs.fetchone()
        num = rs[0]
        return num

    # get count of the actuation for in the table.
    def get_data_cnt(self, table_name):
        sql = "SELECT count(*) FROM " + self.DBN_dm + "." + table_name + "_act;"
        # print("dbm >> ", sql)
        self.curs.execute(sql)
        rs = self.curs.fetchone()
        num = rs[0]
        #print("dbm >> ", num)
        
        self.conn.commit()

        return num

    # get a list of acutators which have an actuating event.
    def get_distinct_actlist(self, table_name):
        sql = "SELECT DISTINCT actuator FROM " + self.DBN_dm + "." + table_name + "_act;"
        #print("dbm >> ", sql)
        self.curs.execute(sql)
        act = self.curs.fetchall()
        newlist = [data[0] for data in act]
        return newlist

    # get newest key:value pair of the actuator
    def get_keyValue_act(self, actuator, table_name):
        sql = "SELECT actuator, status FROM " + self.DBN_dm + "." + table_name + "_act WHERE actuator='" + actuator + \
                                "' order by timestamp desc limit 1;"
        print("dbm >> ", sql)
        self.curs.execute(sql)
        rs = self.curs.fetchone()
        return rs

    # delete actuator event after sending actuating message to device
    def delete_actuator_data(self, actuator, table_name):
        sql = "DELETE FROM " + self.DBN_dm + "." + table_name + "_act WHERE actuator='" + actuator + "';"
        #print("dbm >> ", sql)
        self.curs.execute(sql)
        self.conn.commit()

    # insert sensor data to sensor table
    def insert_data(self, input_list, table_name):
        DB_sql = 'INSERT INTO ' + self.DBN_dm + '.' + table_name + ' ( timestamp, '
        # key
        for i in range(len(input_list)):
            key = input_list[i][0]
            if i == len(input_list) - 1:
                DB_sql = DB_sql + key
            else:
                DB_sql = DB_sql + key +', '
        DB_sql = DB_sql[:len(DB_sql)] + ') VALUES (now(), '

        # value
        for i in range(len(input_list)):
            value = input_list[i][1]
            if i == len(input_list)-1:
                DB_sql = DB_sql + "'" + value + "'"
            else:
                DB_sql = DB_sql + "'" + value + "',"
        DB_sql = DB_sql + ');'
        print(DB_sql)
        self.curs.execute(DB_sql)
        self.conn.commit()