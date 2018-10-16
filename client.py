#!/usr/bin/env python3

import sys
import socket
from typing import Dict

import ftplib
# TODO parse args for file name, host, and port - use host/port from transfer.main?
FILE = sys.argv[1:]  # TODO move to main? parse other args . . .


# Client initiates file request from server
class SimpleFTPClient:

    def __init__(self, host_address=ftplib.HOST, port=ftplib.PORT):
        self._received = bytearray()  # encapsulate ?
        self._received_length = 0
        self._packet_length = 0

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setblocking(False)
            # Connect to server and send file request
            sock.connect((host_address, port))
            # TODO create packet w/client-specific header and send to server
            sock.send()
            # Check if data sent so far is all there is for the file? - check if "final-packet" is 1/True in header keys
            while True:
                # Receive data from the server and send packet confirmation once entire packet is received
                data = sock.recv(ftplib.BUFFER_SIZE)
                # extract following into method and put into ftplib . . .
                if data:  # non-zero number of bytes were received
                    self._received_length += len(data)
                    # TODO process _received data - convert data to sys.byteorder on client host - check "byteorder" key
                    self._received += data
                    # TODO check for closing message from server . . .
                    pass
                if self._received_length == self._packet_length:
                    # TODO send confirmation to server so it can send the next packet
                    #      TODO add computed checksum so server can verify!
                    pass

    @staticmethod  # TODO move to ftp_lib - create_client_header() ?
    def create_header(file_name=None) -> Dict:  # append dict to create_packet dict?
        # TODO add packet content checksum, all verified server-side via client confirmation packets
        header = {"checksum": None}
        if file_name is not None:
            header.update({"file-name": file_name})
        return header
