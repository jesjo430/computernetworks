#!/usr/bin/python
#Proxy handler

from threading import Thread
import sys, socket

MAX_CONNECTIONS = 10 #Max buffer in connection
BUFFER_SIZE = 2048 #Amount of data to handle in chunks
HOST = ('127.0.0.1',8001) #Temp 
BAD_URL_REDIR_PAGE = "http://zebroid.ida.liu.se/error1.html"
BAD_CONTENT_REDIR_PAGE = "http://zebroid.ida.liu.se/error2.html"
BAD_CONTENT_HOST = "zebroid.ida.liu.se"
BAD_CONTENT = {b'SpongeBob', b'Britney Spears', b'Paris Hilton', b'Norrk?ping'}

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
    print("\n" + "DATA: \n" + str(data) + "\n")
    if has_bad_content(data):
        data = filter_url(data)

    try:
        webserver = str(get_host(data), "utf-8")
        print("WEBSERVER: " + webserver + "\n")

        proxy_server(webserver, 80, conn_client, addr, data)
    except Exception as e:
        print("Something went wrong when reading:\n")
        print(e)
        sys.exit()

def proxy_server(webserver, port, conn_client, addr, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((webserver, port))
        print("PROXY CONNECTED TO WEBSERVER, SENDING DATA...\n")
        s.send(data)

        #Look for answer from webserver
        while 1:
            try:    
                answer = s.recv(BUFFER_SIZE)
                if (len(answer)>0): #If any
                    print(answer + b'\n')
                    if (is_text(answer) and has_bad_content(answer)):
                        answer = filter_content(s, webserver, data)

                    conn_client.send(answer) #send it to user
                    print("Content accepted")
            except socket.timeout as message:
                print("End of recv \n")
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

def get_host(data):
    second_line = data.splitlines()[1]
    url = second_line.split(b' ')[1]
    return url

def get_url(data):
    request = data.split(b' ')[1]
    request = request.split(b' ')[0]
    return request

def has_bad_content(content):
    for bad_word in BAD_CONTENT:
        if bad_word.lower() in content.lower():
            print("Bad content found! \n")
            return True
    return False

def type_of_content(content):
    content = content.split(b'Content-Type:')[1]
    content_type = content.split(b'\r')[0]
    print(content_type + b'\n')
    return content_type

def is_text(answer):
    if (b'Content-Type' in answer):
        if (b'text' in type_of_content(answer)):
            return True
    return False

def filter_content(s, webserver, data):            
    data = data.replace(webserver.encode("utf-8"), BAD_CONTENT_HOST.encode("utf-8"))
    data = data.replace(get_url(data), BAD_CONTENT_REDIR_PAGE.encode("utf-8"))
    print("This is the new data: \n" + str(data) + "\n")
    s.send(data)
    answer = s.recv(BUFFER_SIZE)
    return answer

def filter_url(data):            
    data = data.replace(get_host(data), BAD_CONTENT_HOST.encode("utf-8"))
    data = data.replace(get_url(data), BAD_URL_REDIR_PAGE.encode("utf-8"))
    print("This is the new data: \n" + str(data) + "\n")
    return data

start()