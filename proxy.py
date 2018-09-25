#!/usr/bin/python
#Proxy handler

from server import Server
from threading import Thread
import sys, socket

MAX_CONNECTIONS = 10 #Max buffer in connection
BUFFER_SIZE = 2048 #Amount of data to handle in chunks
HOST = ('127.0.0.1',8001) #Temp 
BAD_CONTENT_REDIR_PAGE = "http://zebroid.ida.liu.se/error1.html"
BAD_CONTENT = {"SpongeBob", "Britney Spears", "Paris Hilton", "Norrk?ping"}

try:
    listen_port = 8001
    #int(raw_input("Enter port number: ")) #User input for chosing port
except KeyboardInterrupt:
    print("\nShutting down...")
    sys.exit()

def start():
    #************************** INIT ****************************#
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Init socket as TCP
        s.bind(HOST) #Bind port to listen at
        s.listen(MAX_CONNECTIONS) #Start listen 
        print("Server listening at " + str(HOST))
    except Exception as e:
        print("Failed to start before setup:")
        print(e)
        sys.exit(1)

    #***************** Waiting for client req. *******************#
    while 1:
        try:
            conn_client, addr = s.accept() #Accept connection from workstation
            data = conn_client.recv(BUFFER_SIZE) # Recieve data from user
            t1 = Thread(target=conn_thread, args=[conn_client, data, addr])
            t1.start()
            t1.join()
        except KeyboardInterrupt:
            conn_client.close()
            s.close()
            print("Closing proxy while trying to accept...")
            sys.exit(1)
    s.close()

def conn_thread(conn_client, data, addr):
    try:
        print("\n" + "DATA: " + str(data) + "\n")
        webserver = get_url_from_req(data)
        print("WEBSERVER: " + webserver + "\n")

        proxy_server(webserver, 80, conn_client, addr, data)
    except Exception as e:
        print("Something went wrong when reading:\n")
        print(e)
        sys.exit()

def proxy_server(webserver, port, conn_client, addr, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        print("PROXY CONNECTED TO WEBSERVER, SENDING DATA...\n")
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
        print("Done")
    except socket.error as message:
        print("Socket exited when trying to send:")
        print(message)
        #print(value)
        s.close()
        conn_client.close()
        sys.exit(1)
    sys.exit(0)

def get_url_from_req(data):
    second_line = str(data.splitlines()[1], "utf-8")
    url = second_line.split(" ")[1]
    return url

def has_bad_content(content):
    for bad_word in BAD_CONTENT:
        if bad_word in content:
            return True
    return False

start()