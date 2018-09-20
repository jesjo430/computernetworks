#!/usr/bin/python
#Proxy handler

from server import Server
from thread import start_new_thread
import sys, socket

MAX_CONNECTIONS = 5 #Max buffer in connection
BUFFER_SIZE = 2048 #Amount of data to handle in chunks
PROXY_HOST = ('127.0.0.1',8001) #Temp
DEBUG = True

try:
    listen_port = 8001
    #int(raw_input("Enter port number: ")) #User input for chosing port
except KeyboardInterrupt:
    print "\n[*] Shutting down..."
    sys.exit()

def start():
    #************************** INIT ****************************#
    try:
        if DEBUG: print "Creating socket for proxy server...\n"
        conn_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Init socket as TCP
        if DEBUG: print "Binding socket...\n"
        conn_server.bind(PROXY_HOST) #Bind port to listen at
        conn_server.listen(MAX_CONNECTIONS) #Start listen 
        print "Proxy listening at " + str(PROXY_HOST)
    except Exception, e:
        print "[*] Failed to start before setup"
        print e.message
        sys.exit(1)

    #***************** Waiting for client req. *******************#
    while 1:
        try:
            if DEBUG: print "\nWaiting for request...\n"
            conn_client, addr = conn_server.accept() #Accept connection from workstation
            if DEBUG: print "Recieving "+ str(BUFFER_SIZE) + "bytes from socket...\n"
            client_request = conn_client.recv(BUFFER_SIZE) # Recieve data from user
            if DEBUG: print "Creating new thread..."
            start_new_thread(conn_client_thread, (conn_client, client_request, client_request)) #Start new thread to handle request from user
        except KeyboardInterrupt:
            print "[*] Closing proxy while trying to accept..."
            sys.exit(1)
    conn_server.close()

def conn_client_thread(conn_client, client_request, addr):
    try:
        if DEBUG: print "Handling request...:"
        print client_request
        host = get_host(client_request)
        print "Connecting to Host: " + host

        if DEBUG: print "Creating proxy client socket\n"
        proxy_server(host, 80, conn_client, addr, client_request)
    except Exception, e:
        print "[*] Something went wrong when reading:\n"
        print e.message
        sys.exit()

def proxy_server(host, port, conn_client, addr, client_request):
    try:
        conn_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Connecting to:\n"
        print host
        print port

        print "[*] I got here!"
        conn_server.connect((host, port)) #Crashes....
        print "[*] But not here!..."

        conn_server.send(client_request)

        #Look for answer from host
        while 1:
            if DEBUG: print "Recieving answer from: " + host + "...\n"
            answer = conn_server.recv(BUFFER_SIZE)
            if (len(answer)>0): #If any
                if DEBUG: print "Sending answer to user...\n"
                conn_client.send(answer) #send it to user
            else: # No return message (left)
                break
        conn_server.close() # Close server socket
        conn_client.close() #Close client socket, no more data
    except socket.error, (value, message):
        print "[*] Socket exited when trying to send because"
        print message
        print value
        if DEBUG: print "[*] Closing all sockets...\n"
        conn_server.close()
        conn_client.close()
        if DEBUG: print "[*] Killing thread badly...\n"
        sys.exit(1)
    if DEBUG: print "[*] Killing thread in a good way...\n"
    sys.exit(0)

def get_host(data):
    second_line = data.split('\n')[1]
    url = second_line.split(' ')[1]
    return url

start()