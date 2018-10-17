#!/usr/bin/env python3

import socket
import ftplib
# TODO --bind and --directory options (https://docs.python.org/3/library/http.server.html) ?
# TODO handle OSErrors


# Server sends binary file specified by client upon request
class BinaryFTPServer:

    def __init__(self):
        self.request = None
        self.client_address = None
        self.packet = ftplib.PacketData()
        self._requested_file = None
        self._file_offset = 0  # number of bytes
        self._awaiting_confirmation = False
        # self.request.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.request.setblocking(False)

    def startup(self, host_address=ftplib.HOST, port=ftplib.PORT):  # Default: host_address='localhost', port=64000
        # Create the server, binding to 'host_address' on 'port'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host_address, port))
            sock.listen()
            print("listening . . .")
            self.request, self.client_address = sock.accept()
            with self.request:
                print("Connected by: ", self.client_address)
                while True:
                    if self._awaiting_confirmation or self._requested_file is None:  # need to recv data from client
                        try:
                            data = self.request.recv(ftplib.BUFFER_SIZE)  # self.request is the TCP socket connected to the client
                        except BlockingIOError:
                            pass
                        else:
                            if data:
                                self.packet.buffer.append(data)
                                ftplib.process_packet(self.packet)

                                if self.packet.content is not None:
                                    action = self.packet.header['action']

                                    if self._requested_file is None:  # process initial client request
                                        if action == 'START-REQUEST':
                                            # cast to str? or use bytearray.decode() func?
                                            self._requested_file = ftplib.decode(self.packet.content)
                                            self.packet.reset()
                                        else:
                                            raise ValueError('invalid packet: no file has been requested')

                                    elif self._awaiting_confirmation:  # process client confirmation packet
                                        if action == 'CONFIRM':
                                            if self.packet.checksum != ftplib.decode(self.packet.content):
                                                raise ValueError('corrupted packet: mismatched checksum detected')
                                            self._awaiting_confirmation = False  # send next packet w/binary file data . . .
                                            self.packet.reset()
                                        else:
                                            raise ValueError('invalid packet: no verification has been requested')
                            else:
                                raise RuntimeError('No FTP packet sent from client')  # necessary?

                    # Wait for confirmation before sending next FTP packet
                    if self._requested_file is not None and not self._awaiting_confirmation:
                        with open(self._requested_file, 'rb') as f:
                            f.seek(self._file_offset)
                            file_data = f.read(ftplib.BUFFER_SIZE - ftplib.PROTO_HEADER_LENGTH)
                            self._file_offset = f.tell()

                        if not file_data:  # no data left, server has met EOF
                            file_checksum = ftplib.file_md5sum(self._requested_file)
                            ftp_packet = ftplib.create_packet(bytes(file_checksum), action='END-REQUEST')
                            self._file_offset = 0
                            self._requested_file = None
                            self._awaiting_confirmation = False
                            self.packet.buffer = bytearray()
                            self.packet.reset()
                        else:
                            self.packet.checksum = ftplib.packet_md5sum(file_data)
                            ftp_packet = ftplib.create_packet(file_data, action='RECEIVE')
                            self._awaiting_confirmation = True

                        self.request.send(ftp_packet)


if __name__ == "__main__":
    # TODO parse sys.args, cast port# to int, send to startup()
    BinaryFTPServer().startup()
