import io
import sys
import json
import struct
import socket
import socketserver
import hashlib
from types import SimpleNamespace
from typing import Dict, Union

# Library for implementing any of the necessary File Transfer Protocols used to transfer the binary file.
# Binary File Transfer Protocol:
#     TCP:
#         - in-order data and reliable transmission
#         - timeout/retries should be specified, and requesting specific chunks from the file may be supported
#     Header Specifications:
#         - byteorder: system's network byteorder (endian-ness)
#         - action: 'START-REQUEST' | 'END-REQUEST' | 'CONFIRM' | 'RECEIVE'
#         - content-length: length of packet content
#     Action Specifications:
#         - 'START-REQUEST': initiates file transfer request; packet content is the file's name
#         - 'END-REQUEST': ends file transfer request; packet content is the file's checksum for client verification
#         - 'RECEIVE': meant for the client; packet content is a BUFFER_SIZE large file chunk
#         - 'CONFIRM': meant for the server; packet content is the checksum of
#                      the most recently sent packet content (to be verified server-side)

HOST, PORT = '127.0.0.1', 64000  # defaults
BUFFER_SIZE = 4096
PROTO_HEADER_LENGTH = 2  # bytes
ENCODING = 'utf-8'
REQUIRED_HEADERS = {'byteorder', 'content-length', 'action'}  # change these to enum/namedtuple/etc.
ACTIONS = {'START-REQUEST', 'END-REQUEST', 'CONFIRM', 'RECEIVE'}  # add RESEND/REPEAT action if verification fails?


class PacketData(SimpleNamespace):

    def __init__(self):
        super(PacketData, self).__init__()
        self.buffer = bytearray()
        self.checksum = None  # updated per-packet, client checks for server-side verification . . .
        self.header_len = None
        self.header = None
        self.content = None

    def reset(self):
        self.content = None
        self.header = None
        self.header_len = None
        self.checksum = None


# Sadly, this only processes one file/client at a time . . .
class BinaryFTPHandler(socketserver.BaseRequestHandler):  # TODO move this to server module ?
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def __init__(self, *args, **kwargs):
        super(BinaryFTPHandler, self).__init__(*args, **kwargs)
        self.packet = PacketData()
        self._requested_file = None
        self._file_offset = 0  # number of bytes
        self._awaiting_confirmation = False
        self.request.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.request.setblocking(False)

    def handle(self):
        if self._awaiting_confirmation or self._requested_file is None:  # need to recv data from client
            try:
                data = self.request.recv(BUFFER_SIZE)  # self.request is the TCP socket connected to the client
            except BlockingIOError:
                pass
            else:
                if data:
                    self.packet.buffer.append(data)
                    process_packet(self.packet)

                    if self.packet.content is not None:
                        action = self.packet.header['action']

                        if self._requested_file is None:  # process initial client request
                            if action == 'START-REQUEST':
                                # cast to str? or use bytearray.decode() func?
                                self._requested_file = decode(self.packet.content)
                                self.packet.reset()
                            else:
                                raise ValueError('invalid packet: no file has been requested')

                        elif self._awaiting_confirmation:  # process client confirmation packet
                            if action == 'CONFIRM':
                                if self.packet.checksum != decode(self.packet.content):
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
                file_data = f.read(BUFFER_SIZE - PROTO_HEADER_LENGTH)
                self._file_offset = f.tell()

            if not file_data:  # no data left, server has met EOF
                file_checksum = file_md5sum(self._requested_file)
                ftp_packet = create_packet(bytes(file_checksum), action='END-REQUEST')
                self._file_offset = 0
                self._requested_file = None
                self._awaiting_confirmation = False
                self.packet.buffer = bytearray()
                self.packet.reset()
            else:
                self.packet.checksum = packet_md5sum(file_data)
                ftp_packet = create_packet(file_data, action='RECEIVE')
                self._awaiting_confirmation = True

            self.request.send(ftp_packet)


def process_proto_header(packet: PacketData):
    if len(packet.buffer) >= PROTO_HEADER_LENGTH:
        packet.header_len = struct.unpack(">H", packet.buffer[:PROTO_HEADER_LENGTH])[0]
        packet.buffer = packet.buffer[PROTO_HEADER_LENGTH:]


def process_header(packet: PacketData):
    if len(packet.buffer) >= packet.header_len:
        packet.header = decode(packet.buffer[:packet.header_len])
        if any(hdr not in packet.header for hdr in REQUIRED_HEADERS):
            raise ValueError("invalid packet: missing required header")
        if packet.header['action'] not in ACTIONS:
            raise ValueError(f"invalid packet: invalid action specification '{packet.header['action']}'")
        packet.buffer = packet.buffer[packet.header_len:]


def process_content(packet: PacketData):
    content_len = packet.header['content-length']
    if len(packet.buffer) < content_len:
        return
    packet.content = packet.buffer[:content_len]
    packet.buffer = packet.buffer[content_len:]


def process_packet(packet: PacketData):
    if packet.header_len is None:  # process proto-header
        process_proto_header(packet)

    if packet.header_len is not None:  # process packet header
        if packet.header is None:
            process_header(packet)

    if packet.header is not None:  # process packet content
        if packet.content is None:
            process_content(packet)


def encode(packet_data):
    return json.dumps(packet_data, ensure_ascii=False).encode(ENCODING)


def decode(packet_data):
    tiow = io.TextIOWrapper(io.BytesIO(packet_data), encoding=ENCODING, newline='')  # is this necessary?
    header = json.load(tiow)  # why can't I call load on ftp_packet_header directly? . . .
    tiow.close()
    return header


def create_packet(packet_content: Union[bytes, bytearray], action: str, additional_headers: Dict = None):
    header = {
        "byteorder": sys.byteorder,  # remove/specify '>' (big-endian)?
        "action": action,
        "content-length": len(packet_content)
    }
    if additional_headers is not None:
        header.update(additional_headers)
    packet_header = encode(header)
    proto_header = struct.pack(">H", len(packet_header))
    message = proto_header + packet_header + packet_content
    return message


def packet_md5sum(data: Union[bytes, bytearray]):
    return hashlib.md5(data).hexdigest()


def file_md5sum(filename: str):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
