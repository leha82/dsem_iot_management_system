#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import TcpServer
import json

server = TcpServer.TcpServer()
file_path = './config.json'
with open(file_path, "r") as fj:
    fd = json.load(fj)
    a = fd['PORT']
    b = fd['DB_Host']
    c = fd['DB_User']
    d = fd['DB_password'] 
    e = fd['DeviceRegistry_DB_name']
    f = fd['Sensor_DB_name']
    g = fd['Specific_table_name']
    h = fd['Device_Register_table_name']
server=TcpServer.TcpServer(a,b,c,d,e,f,g,h)
server.DB_Con()
server.run()
