#!/usr/bin/python
#TCP_server script

import socket

class Server:
    def init_socket():
        sock = socket.socket()
        host = socket.gethostname()
        sock.bind((host, port))

    def recieve_all():
        data = null
        while data:

    def close_connection():
        conn.close()

    def open_connection():
        conn, addr = sock.accept()