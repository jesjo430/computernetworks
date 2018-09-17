#!/usr/bin/python
#Proxy handler

import Server
import sys

MAX_CONNECTIONS = 5

# Start-up
input_port = input("Enter port number for proxy: ")
#Todo: Make sure input is correct. 
PROXY_PORT = input_port

# Init new server
server = Server()
server.init_socket(PROXY_PORT)

# Listen
    server.listen(MAX_CONNECTIONS)

