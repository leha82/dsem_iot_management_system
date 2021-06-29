
# 외부 모듈 socket 사용함으로 설치해줄 것
# 다른 버전의 PYthon 작동은 확인 안 해봄 
import socket
Receive_Buffersize = 4096

def ipcheck():
    return socket.gethostbyname(socket.getfqdn())

class TcpNet:
    def __init__(self): # 생성자
        self.com_socket=socket.socket() # 소켓객체생성
        self.Connection=self.com_socket # 소캣이랑 연결하기

    def Accept(self,IP,Port): # 주소랑 포트에 열어주기
        self.com_socket.bind((IP,Port))
        self.com_socket.listen(10)
        self.Connection, self.address = self.com_socket.accept()

    def Connect(self,IP,Port): # 그 주소의 포트에 연결하기
        self.com_socket.connect((IP,Port))

    def Send(self,bdta): # 보내기 (binary) 형식임으로 주의할 것
        self.Conncetion.send(bdta) 

    def SendStr(self,Str1): # 보내기 String 형식으로 보내기
        self.Connection.send(bytes(Str1,"UTF-8"))

    def Receive(self): # 받기 (binary) 형식임으로 주의할 것
        return self.Connection.recv(Receive_Buffersize)

    def ReceiveStr(self): # 받기 String 형식으로 받기
        return self.Connection.recv(Receive_Buffersize).decode("UTF-8")

    def Socket_close(self): # 소켓 닫기 (미완성)
        self.address.close()

    def GetHostIP():
        return socket.gethostbyname(socket.getfqdn())




