#!/usr/bin/python
#TCP_server script

import socket


class Server:
    def __init__(self, sock):
        self.sock = sock

    # Initialize a TCP socket.
    def init_socket(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        sock.bind((host, port))

    def close_connection(self):
        conn.close()

    def open_connection(self):
        conn, addr = sock.accept()