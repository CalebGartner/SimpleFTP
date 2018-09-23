#!/usr/bin/env python3

import socket

HOST = 'local_host'
PORT = 9528
BUFFER = 4096
FILE = ''

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    with open(FILE, 'rb') as binary_data:
        s.sendfile(binary_data)  # buffer size is heuristically determined based on FILE
