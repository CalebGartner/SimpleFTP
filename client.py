#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'
PORT = 64000


class SimpleClient:

    @staticmethod
    def startup(file_name: str):
        with socket.socket() as s, open(file_name, 'rb') as binary_data:
            s.connect((HOST, PORT))
            s.sendfile(binary_data)  # buffer size is heuristically determined based on FILE
