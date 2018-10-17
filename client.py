#!/usr/bin/env python3

import sys
import socket

import ftplib
FILE: str = "test.png"  # default
# TODO make host/port/file configurable


# Client initiates file request from server
class SimpleFTPClient:

    def __init__(self):
        self.packet = ftplib.PacketData()

    def startup(self, host_address=ftplib.HOST, port=ftplib.PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # sock.setblocking(False)
            # Connect to server and send file request
            sock.connect((host_address, port))
            ftp_request = ftplib.create_packet(FILE, action='START-REQUEST')
            sock.send(ftp_request)
            while True:
                try:  # Receive data from the server and send packet confirmation once entire packet is received
                    data = sock.recv(ftplib.BUFFER_SIZE)
                except BlockingIOError:
                    pass
                else:
                    if data:  # non-zero number of bytes were received
                        self.packet.buffer += data
                        ftplib.process_packet(self.packet)

                        if self.packet.content is not None:
                            action = self.packet.header['action']

                            if action == 'RECEIVE':  # process received file data
                                with open(FILE, 'ab', encoding=ftplib.ENCODING) as f:
                                    f.write(self.packet.content)
                                checksum = ftplib.packet_md5sum(self.packet.content)
                                confirmation_packet = ftplib.create_packet(checksum, action='CONFIRM')
                                sock.send(confirmation_packet)
                                self.packet.reset()

                            elif action == 'END-REQUEST':  # verify checksum and exit loop
                                file_checksum = ftplib.file_md5sum(FILE)
                                if file_checksum == ftplib.decode_header(self.packet.content):
                                    print(f"success! '{FILE}' has been transferred without incident")
                                    break
                                else:
                                    raise ValueError('corrupted file: transfer failed: mismatched checksum detected')
                            else:
                                raise ValueError(f"invalid packet: invalid action '{action}' specified for client")


if __name__ == '__main__':
    # TODO parse args for file name, host, and port - use host/port from transfer.main?
    # FILE = sys.argv[1:]  # TODO move to main? parse other args . . .
    SimpleFTPClient().startup()
