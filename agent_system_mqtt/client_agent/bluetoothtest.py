import bluetooth as bt

#adress="98:D3:51:FD:B7:C7"
adress="20:13:06:18:10:53"
port=1
    
bt_socket=bt.BluetoothSocket(bt.RFCOMM)
print("{0}, {1}".format(adress,port))

bt_socket.connect((adress,port))