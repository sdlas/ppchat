# -*- coding:utf8 -*-
import threading
import hashlib
import socket
import base64
#socket端口信息
HOST='172.17.0.10'
PORT=50001

#存放中转信息
web_to_socket = [] 
socket_to_web = []

#接收websocket消息线程
class websocketget_thread(threading.Thread):
    def __init__(self, connection):
        super(websocketget_thread, self).__init__()
        self.connection = connection
 
    def run(self):
        global web_to_socket
        global socket_to_web
        while True:
            data = self.connection.recv(1024)
            if data:
                print 'data from websocket---->'
                print parse_data(data)
                data = parse_data(data)
                web_to_socket.append(data)
        self.connection.close()

#向websocket推送消息线程
class websocketsend_thread(threading.Thread):
    def __init__(self, connection):
        super(websocketsend_thread, self).__init__()
        self.connection = connection
 
    def run(self):
        global web_to_socket
        global socket_to_web
        while True:
            if socket_to_web:
                msg = socket_to_web.pop()
                self.connection.send('%c%c%s' % (0x81, len(msg), msg))
        self.connection.close()

#接收socket信息线程            
class socketget_thread(threading.Thread):
    def __init__(self,conn,addr):
        super(socketget_thread, self).__init__()
        self.conn = conn
        self.addr = addr
    def run(self):
        global web_to_socket
        global socket_to_web
        while True:
            data=self.conn.recv(1024)    #把接收的数据实例化
            if data:
                print 'data from socket---->'
                print data
                print type(data)
                socket_to_web.append(data)
        self.conn.close()

#向推送socket推送信息线程            
class socketsend_thread(threading.Thread):
    def __init__(self,conn,addr):
        super(socketsend_thread, self).__init__()
        self.conn = conn
        self.addr = addr
    def run(self):
        global web_to_socket
        global socket_to_web
        while True:
            if web_to_socket:
                msg = web_to_socket.pop()
                print("msg.encode",msg)
                self.conn.sendall(msg)
        self.conn.close()

def parse_data(msg):
    v = ord(msg[1]) & 0x7f
    if v == 0x7e:
        p = 4
    elif v == 0x7f:
        p = 10
    else:
        p = 2
    mask = msg[p:p + 4]
    data = msg[p + 4:]
    return ''.join([chr(ord(v) ^ ord(mask[k % 4])) for k, v in enumerate(data)])
def parse_headers(msg):
    headers = {}
    header, data = msg.split('\r\n\r\n', 1)
    for line in header.split('\r\n')[1:]:
        key, value = line.split(': ', 1)
        headers[key] = value
    headers['data'] = data
    return headers
def generate_token(msg):
    key = msg + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    ser_key = hashlib.sha1(key).digest()
    return base64.b64encode(ser_key)
 
 
if __name__ == '__main__':
    #websocket初始化
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.setsockopt(level,optname,value) 设置给定套接字选项的值。
    #打开或关闭地址复用功能。当option_value不等于0时，打开，否则，关闭。它实际所做的工作是置sock->sk->sk_reuse为1或0。
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('172.17.0.10', 50000))
    print '开始websocket监听'
    sock.listen(5)
    #首先，我们创建了一个套接字，然后让套接字开始监听接口，并且最多只能监听5个请求
    while True:
        connection, address = sock.accept()
	    #接受监听到的连接请求，
        print address
        try:
            data = connection.recv(1024)
            headers = parse_headers(data)
            token = generate_token(headers['Sec-WebSocket-Key'])
            connection.send('\
HTTP/1.1 101 WebSocket Protocol Hybi-10\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n' % (token))
            thread1 = websocketget_thread(connection)
            thread2 = websocketsend_thread(connection)
            break
        except socket.timeout:
            print 'websocket connection timeout'
    #websocket
    s= socket.socket(socket.AF_INET,socket.SOCK_STREAM) #定义socket类型，网络通信，TCP
    s.bind((HOST,PORT)) #套接字绑定的IP与端口
    print '开始TCP监听'
    s.listen(1) #开始TCP监听,监听1个请求
    conn,addr=s.accept()   #接受TCP连接，并返回新的套接字与IP地址
    thread3 = socketget_thread(conn,addr)
    thread4 = socketsend_thread(conn,addr)
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    