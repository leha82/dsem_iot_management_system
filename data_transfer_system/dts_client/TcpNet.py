import socket
Buffer_Size = 4096
class TcpNet:
    def __init__(self):
        self.com_socket =socket.socket()
        self.Connection=self.com_socket
    def Accept(self, IP, Port):
        self.com_socket.bind((IP,Port))
        self.com_socket.listen(10);
        self.Connection, self.address = self.com_socket.accept()
    def Connect(self,IP,Port):
        self.com_socket.connect((IP,Port))
    def Send(self,bdta):
        self.Connection.send(bdta)
    def SendStr(self,Str1):
        self.Connection.send(bytes(Str1,"UTF-8"))
    def Receive(self):
        return self.Connection.recv(Buffer_Size)
    def ReceiveStr(self):
        return self.Connection.recv(Buffer_Size).decode("UTF-8")
    def Close(self):
        self.com_socket.close()
        