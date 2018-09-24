#!/usr/bin/env python3

import socket

HOST = 'local_host'
PORT = 9500


class Client:

    @staticmethod
    def startup(file_name: str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            with open(file_name, 'rb') as binary_data:
                s.sendfile(binary_data)  # buffer size is heuristically determined based on FILE
