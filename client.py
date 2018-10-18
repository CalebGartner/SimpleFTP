#!/usr/bin/env python3

import os
import socket

import ftplib
DIR = os.path.dirname(os.path.abspath(__file__))  # default
FILE: str = "test.png"  # default - remove/move to ftplib ?
# TODO make host/port/file configurable - opt/argparse module


class BinaryFTPClient:  # Client initiates file request from server

    _socket: socket

    def __init__(self):
        self.packet = ftplib.PacketData()
        self._socket = None

    def startup(self, host_address=ftplib.HOST, port=ftplib.PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self._socket:
            self._socket.connect((host_address, port))  # Connect to server and send file request

            # TODO check if specified file already exists in DIR
            ftp_request = ftplib.create_packet(FILE, action=ftplib.ACTIONS.START_REQUEST)
            self._socket.send(ftp_request)
            while True:
                try:  # Receive data from the server and send packet checksum once entire packet is received
                    data = self._socket.recv(ftplib.BUFFER_SIZE)
                except BlockingIOError:
                    pass
                else:
                    if data:  # Non-zero number of bytes were received
                        self.packet.buffer += data
                        ftplib.process_packet(self.packet)

                        if self.packet.content is not None:
                            action = self.packet.header[ftplib.HEADERS.ACTION]

                            if action == ftplib.ACTIONS.RECEIVE:  # Process received file data
                                self.do_RECEIVE()
                            elif action == ftplib.ACTIONS.END_REQUEST:  # Verify file checksum and exit
                                self.do_END_REQUEST()
                                break
                            else:
                                raise ValueError(f"invalid action '{action}' specified for client")

    def do_RECEIVE(self):  # TODO once received dir is specified, copy to dir
        with open(os.path.join(DIR, 'copy_of_' + FILE), 'ab') as f:  # Append received data to file
            f.write(self.packet.content)

        checksum = ftplib.packet_md5sum(self.packet.content)
        confirmation_packet = ftplib.create_packet(checksum, action=ftplib.ACTIONS.CONFIRM)
        self._socket.send(confirmation_packet)

        self.packet.reset()

    def do_END_REQUEST(self):
        file_checksum = ftplib.file_md5sum(FILE)
        if file_checksum == ftplib.decode(self.packet.content):
            print(f"Success! '{FILE}' has been transferred without incident . . .")
        else:
            raise ValueError('corrupted file: transfer failed: mismatched checksum detected')


if __name__ == '__main__':
    # TODO parse args for file name, host, and port
    BinaryFTPClient().startup()
