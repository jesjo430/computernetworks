#!/usr/bin/python
#TCP_server script

import socket

s = socket.socket()
host = socket.gethostname()
port = 9999

s.bind((host,port))

print "Waiting for connection..."
s.listen(5)

while True:
    conn,addr = s.accept()
    print 'Got connection from ', addr
    conn.send('Server saying Hi')
    conn.close()