#!/usr/bin/env python3

import ftplib
import socket
import sys

FILE = sys.argv[1:]  # TODO move to main?


class SimpleClient:

    def __init__(self, host_address=ftplib.HOST, port=ftplib.PORT):
        # TODO parse args for file name, host, and port - use host/port from transfer.main?

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((host_address, port))
            # TODO open file in binary mode 'rb', parse into BUFFER_SIZE - 2 - <header length> chunks, send each chunk
            # Do I need to get confirmation of each chunk?
            # TODO use struct to calculate size of chunk/msg, pack integer result into 2 bytes via format string
            #      and prepend to chunk as header
            sock.sendall(bytes(data + "\n", "utf-8"))

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")

    print("Sent:     {}".format(data))
    print("Received: {}".format(received))