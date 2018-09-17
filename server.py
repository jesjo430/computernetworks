#!/usr/bin/python
#TCP_server script

import socket

class Server:
    # Initialize a TCP socket. 
    def init_socket(int port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        sock.bind((host, port))

    def recieve_all():
        data = null
        while data:

    def close_connection():
        conn.close()

    def open_connection():
        conn, addr = sock.accept()