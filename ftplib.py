import io
import sys
import json
import struct
import socket
import socketserver
from typing import Dict

# Library for implementing any of the necessary File Transfer Protocols used in to transfer the binary data.
# Binary File Transfer Protocol:
#     TCP:
#         - in-order data and reliable transmission
#         - timeout/retries should be specified, and requesting specific chunks from the file may be supported
#     Header:
#         - total number of chunks in file
#         - specific chunk number (shouldn't be necessary since TCP sends data in order)
#         - should it send part (x%) of the calculated checksum?
#     Close:
#         - closing message for the server using the FTP should be specified

HOST, PORT = '127.0.0.1', 64000  # defaults
BUFFER_SIZE = 4096
PROTO_HEADER_LENGTH = 2  # bytes
ENCODING = 'utf-8'


# TODO open file in binary mode 'rb', parse into BUFFER_SIZE - 2 - <header length> chunks, send each chunk
# Open at specific point in file if packet checksum fails, retry?

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
        self._data_buffer = bytearray()
        self._requested_file = None
        self._file_offset = 0  # how much of the file has already been transmitted - _file_length variable ?
        self._packet_checksum = ""  # updated per-packet, verified via client confirmation . . .
        self.request.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.request.setblocking(False)
        # TODO state sentinel value? _awaiting_confirmation = False # ... bool ?

    def setup(self):
        super(BinaryFTPHandler, self).setup()

    def finish(self):
        super(BinaryFTPHandler, self).finish()
        # TODO clear self._data_buffer ? if sentinel value is flagged?

    def handle(self):
        # extract some of the following into ftplib . . . ?
        # while self._awaiting_confirmation: self.request.send(<packet>)
        # TODO if self._awaiting_confirmation or self._requested_file is not None: <receive data>
        try:
            data = self.request.recv(BUFFER_SIZE)  # self.request is the TCP socket connected to the client
        except BlockingIOError:
            pass
        else:
            if data:
                self._data_buffer.append(data)
            else:
                raise RuntimeError("No FTP confirmation sent from client")  # necessary?
        # Wait for confirmation before sending next FTP packet
        # TODO calculate checksum/save it, create header, create packet, set _awaiting_confirmation to True, send packet
        # self.request.send()

    @staticmethod  # move to ftplib module ?
    def create_header(final_packet: bool = False, file_checksum=None) -> Dict:
        header = {"final-packet": int(final_packet)}
        if file_checksum is not None:
            header.update({"file-checksum": file_checksum})
        return header


# TODO encode/decode FTP packet methods - FTPPacket class? - process_<part>header method(s) - process_file method?
def encode_header(ftp_packet_header):
    return json.dumps(ftp_packet_header, ensure_ascii=False).encode(ENCODING)


def decode_header(ftp_packet_header):
    tiow = io.TextIOWrapper(io.BytesIO(ftp_packet_header), encoding=ENCODING, newline="")  # is this necessary?
    header = json.load(tiow)  # TODO why can't I call load on ftp_packet_header directly? . . .
    tiow.close()
    return header


def create_packet(packet_content: bytearray, header_updates: Dict):
    # TODO check length of packet ? shouldn't be necessary...
    header = {
        "byteorder": sys.byteorder,
        "content-encoding": ENCODING,
        "content-length": len(packet_content),
    }
    header.update(header_updates)
    packet_header = encode_header(header)
    proto_header = struct.pack(">H", len(packet_header))
    message = proto_header + packet_header + packet_content
    return message
