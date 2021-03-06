#!/usr/bin/python
#Proxy handler

from threading import Thread
import sys, socket
import gzip

MAX_CONNECTIONS = 10 #Max buffer in connection
BUFFER_SIZE = 2048 #Amount of data to handle in chunks

BAD_URL_REDIR_PAGE = "http://zebroid.ida.liu.se/error1.html"
BAD_CONTENT_REDIR_PAGE = "http://zebroid.ida.liu.se/error2.html"
BAD_CONTENT_HOST = "zebroid.ida.liu.se"
BAD_CONTENT = {b'SpongeBob', b'Britney Spears', b'Paris Hilton', b'Norrkoping'}

try:
    listen_port = int(input("Enter port number: ")) #User input for chosing port
    HOST = ('127.0.0.1', listen_port) #Temp 

except KeyboardInterrupt:
    print("\nShutting down...")
    sys.exit()

# Main program, initialises socket and waits for client connection and request.
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

    #***************** Waiting for client request *******************#
    while 1:
        try:
            connect_client, addr = s.accept() #Accept connection from workstation
            data = connect_client.recv(BUFFER_SIZE) # Recieve data from user
            t1 = Thread(target=connect_thread, args=[connect_client, data, addr]) # Creates a new thread
            t1.start()
            t1.join()
        except KeyboardInterrupt:
            connect_client.close()
            s.close()
            print("Closing proxy while trying to accept...")
            sys.exit(1)
    s.close()

# The new thread for handling current connection to given addr. 
def connect_thread(connect_client, data, addr):
    print("\n" + "DATA: \n" + str(data) + "\n")
    if has_bad_content(data):
        data = filter_url(data)

    try:
        webserver = str(get_host(data), "utf-8")
        print("WEBSERVER: " + webserver + "\n")

        proxy_server(webserver, 80, connect_client, addr, data)
    except Exception as e:
        print("Something went wrong when reading:\n")
        print(e)
        sys.exit()

# Connects to the webserver and send data to it, recieve data back from webserver if any.
# Also sends the data back to the workstation.
def proxy_server(webserver, port, connect_client, addr, data):
    try:
        s = create_and_connect_socket(webserver, port)
        print("PROXY CONNECTED TO WEBSERVER, SENDING DATA...\n")
        data = set_accept_encoding(b'identity', data)                    
        s.send(data)
        buffered_answer = b''

        #Look for answer from webserver and send back to workstation if any
        while 1:
            try:    
                latest_answer = s.recv(BUFFER_SIZE)
                buffered_answer += latest_answer
                if (latest_answer == b''):
                    break
            except socket.timeout as message:
                print("End of recv \n")
                if (is_text(buffered_answer) and has_bad_content(buffered_answer)):
                    # If the old response contained bad content we need to close the old socket connected
                    # to the old host(webserver) and open a new one with the BAD_CONTENT_HOST.
                    # We then filter the data, send it to the server and get a new response.
                    s.close()
                    s = create_and_connect_socket(BAD_CONTENT_HOST.encode("utf-8"), port)
                    data = filter_content(webserver, data)
                    s.send(data)
                    buffered_answer = s.recv(BUFFER_SIZE)
                print("Send to workstation: " + str(buffered_answer) + "\n")    
                connect_client.send(buffered_answer) # Send it to workstation
                break
        s.close() # Close server socket
        connect_client.close() # Close client socket, no more data
        print("Done")
    except socket.error as message:
        print("Socket exited when trying to send:")
        print(message)
        s.close()
        connect_client.close()
        sys.exit(1)
    sys.exit(0)

# Gets the host from data.
# Takes a bytes object and returns a bytes object.
def get_host(data):
    second_line = data.splitlines()[1]
    url = second_line.split(b' ')[1]
    return url

# Gets the url from data.
# Takes a bytes object and returns a bytes object.
def get_url(data):
    request = data.split(b' ')[1]
    request = request.split(b' ')[0]
    return request

# Controlls if content contains any of the "bad" words that should be filtered out.
# Takes a bytes object and returns a boolean.
def has_bad_content(content):
    for bad_word in BAD_CONTENT:
        if bad_word.lower() in content.lower():
            print("Bad content found! \n")
            return True
    return False                       

# Checks what content-type the content contains.
# Takes a bytes object and returns a bytes object.
def type_of_content(content):
    content = content.split(b'Content-Type:')[1]
    content_type = content.split(b'\r')[0]
    return content_type

#Takes bytes object as input and and returns bool if contains "Content-Type" field containing "text". 
def is_text(answer):
    if (b'Content-Type' in answer):
        if (b'text' in type_of_content(answer)):
            return True
    return False

# Takes tcp socket, host bytes object webserver and http request byte object data.
# Changes HTTP request data host name and url to BAD_CONTENT_HOST/URL.
# Returns modified http request bytes object.
def filter_content(webserver, data):            
    data = data.replace(webserver.encode("utf-8"), BAD_CONTENT_HOST.encode("utf-8"))
    data = data.replace(get_url(data), BAD_CONTENT_REDIR_PAGE.encode("utf-8"))
    print("This is the new data: \n" + str(data) + "\n")
    return data

# Takes a encoding type and data as bytes object. Returns a new bytes object with the value of the 
# field "Accept-Encoding" changed to enc_type. 
def set_accept_encoding(enc_type, data):
    temp = data.split(b'Accept-Encoding:')[1]
    temp = temp.split(b'\r\n')[0]
    return data.replace(b'Accept-Encoding:' + temp, b'Accept-Encoding: ' + enc_type)

# Takes data, a http request bytes object and changes host and url to BAD_CONTENT_URL/HOST.
# Returns a new http request bytes object. 
def filter_url(data):            
    data = data.replace(get_host(data), BAD_CONTENT_HOST.encode("utf-8"))
    data = data.replace(get_url(data), BAD_URL_REDIR_PAGE.encode("utf-8"))
    print("This is the new data: \n" + str(data) + "\n")
    return data

# Creates a socket with 1 second timeout and connects it to the host from input.
# Returns the socket object.
def create_and_connect_socket(webserver, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect((webserver, port))
    return s

start()