#!/usr/bin/python
#Proxy handler

from server import Server
from thread import start_new_thread
import sys, socket

MAX_CONNECTIONS = 10 #Max buffer in connection
BUFFER_SIZE = 2048 #Amount of data to handle in chunks
HOST = ('127.0.0.1',8001) #Temp 

try:
    listen_port = 8001
    #int(raw_input("Enter port number: ")) #User input for chosing port
except KeyboardInterrupt:
    print "\nShutting down..."
    sys.exit()

def start():
    #************************** INIT ****************************#
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Init socket as TCP
        s.bind(HOST) #Bind port to listen at
        s.listen(MAX_CONNECTIONS) #Start listen 
        print "Server listening at " + str(HOST)
    except Exception, e:
        print "Failed to start before setup:"
        print e.message
        sys.exit(1)

    #***************** Waiting for client req. *******************#
    while 1:
        try:
            conn_client, addr = s.accept() #Accept connection from workstation
            data = conn_client.recv(BUFFER_SIZE) # Recieve data from user
            start_new_thread(conn_thread, (conn_client, data, addr)) #Start new thread to handle request from user
        except KeyboardInterrupt:
            conn_client.close()
            s.close()
            print "Closing proxy while trying to accept..."
            sys.exit(1)
    s.close()

def conn_thread(conn_client, data, addr):
    try:
        print str(data)
        webserver = get_url_from_req(data)
        print webserver

        proxy_server(webserver, 80, conn_client, addr, data)
    except Exception, e:
        print "Something went wrong when reading:\n"
        print e.message
        sys.exit()

def proxy_server(webserver, port, conn_client, addr, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(data)

        #Look for answer from webserver
        while 1:
            answer = s.recv(BUFFER_SIZE)
            if (len(answer)>0): #If any
                conn_client.send(answer) #send it to user
            else: # No return message (left)
                break
        s.close() # Close server socket
        conn_client.close() #Close client socket, no more data
    except socket.error, (value, message):
        print "Socket exited when trying to send:"
        print message
        print value
        s.close()
        conn_client.close()
        sys.exit(1)
    sys.exit(0)

def get_url_from_req(data):
    second_line = data.split('\n')[1]
    url = second_line.split(' ')[1]
    return url

start()