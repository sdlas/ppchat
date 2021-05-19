import socket
import threading
import random
import time
import json
HOST='49.234.220.199'
PORT=50001
client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)      #定义socket类型，网络通信，TCP
client_socket.connect((HOST,PORT))       #要连接的IP与端口
#接收信息线程
class getthread(threading.Thread):
        def __init__(self,client_socket):
                super(getthread, self).__init__()
                self.client_socket = client_socket
        def run(self):
                while True:
                        data = self.client_socket.recv(1024).decode('utf-8')
                        print("收到信息:",data)

#发送信息进程
class sendthread(threading.Thread):
        def __init__(self,client_socket):
                super(sendthread, self).__init__()
                self.client_socket = client_socket
        def run(self):
                while True:
                        envtemperature = 21 + random.randint(3,5)/10
                        soiltemperature = 25 + random.randint(7,9)/10
                        airhumidity = 55 + random.randint(2,4)/10
                        soilhumidity = 23 + random.randint(1,3)/10
                        dataObj = {'envtemperature':envtemperature,'soiltemperature':soiltemperature,'airhumidity':airhumidity,'soilhumidity':soilhumidity}
                        datastr = json.dumps(dataObj)
                        self.client_socket.sendall(datastr.encode())
                        time.sleep(1)

if __name__ == '__main__':
        thread1 = getthread(client_socket)
        thread2 = sendthread(client_socket)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()