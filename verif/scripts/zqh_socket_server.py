#!/usr/bin/python
import socket
 
s = socket.socket()
host = socket.gethostname()
port = 5900
s.bind((host, port))
 
s.listen(1)

cnt = 0
while True:
    (c,addr) = s.accept()
    print(c, addr)
    while True:
        rcv_data = c.recv(1024)
        print(rcv_data)
        send_data = 'server send %0d' %(cnt)
        c.send(send_data)
        cnt = cnt + 1
    c.close()
