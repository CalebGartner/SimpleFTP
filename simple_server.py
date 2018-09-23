#!/usr/bin/env python3
# TODO make client and server into custom classes and compose in 'binary_file_transfer'
# TODO reduce module-level variables
# TODO extract file writing in nested context manager
# TODO calculate checksum at beginning and end to verify integrity
# TODO find/generate test binary file 2-4GB
# TODO status printing - connections, etc.


# uses TCP by default, uses binary encoding by default
import socket

HOST = 'local_host'
PORT = 9528
BUFFER = 4096
FILE = '/path/to/file'
# setnonblocking(0) ?

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    client, addr = s.accept()
    with client:
        print('Connected by', addr)
        while True:
            data = client.recv(BUFFER)
            if not data:
                break
            with open(FILE, 'w+b') as file_copy:
                file_copy.write(data)

