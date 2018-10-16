#!/usr/bin/env python3

import socketserver
import ftplib
# TODO --bind and --directory options (https://docs.python.org/3/library/http.server.html) ?
# TODO handles endian-ness conversion - sys.byteorder?
# TODO handle OSErrors


# Server sends binary file specified by client upon request
class BinaryFTPServer:

    def __init__(self, host_address=ftplib.HOST, port=ftplib.PORT):  # Default: host_address='localhost', port=64000
        # Create the server, binding to 'host_address' on 'port'
        with socketserver.TCPServer((host_address, port), ftplib.BinaryFTPHandler) as server:
            # Activate the server; this will keep running until you interrupt the program with Ctrl+C
            server.serve_forever()


if __name__ == "__main__":
    # TODO parse sys.args, cast port# to int, send to constructor
    BinaryFTPServer()
