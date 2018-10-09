#!/usr/bin/env python3

import socketserver
import ftplib
# TODO --bind and --directory options (https://docs.python.org/3/library/http.server.html)
# TODO handles endian-ness conversion
# TODO handle OSErrors


class BinaryFTPServer:

    def __init__(self, host_address=ftplib.HOST, port=ftplib.PORT):
        # Create the server, binding to localhost on port 64000
        with socketserver.TCPServer((host_address, port), ftplib.BinaryFTPHandler) as server:
            # Activate the server; this will keep running until you interrupt the program with ctrl+C
            server.serve_forever()


if __name__ == "__main__":
    # TODO parse sys.args, cast port# to int, send to constructor
    BinaryFTPServer()
