import socketserver

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
HEADER_LENGTH = 2


class BinaryFTPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        chunk = self.request.recv(BUFFER_SIZE)
        print("{} wrote:".format(self.client_address[0]))
        # just send back the same data, but upper-cased
        self.request.sendall(chunk.upper())


def parse_packet(buffer, extra_param = None):
    pass
