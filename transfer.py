#!/usr/bin/env python3

import server
import client

# TODO use jpg/png file instead
# TODO make host/port/file configurable

# References:
#     - https://realpython.com/python-sockets
#     - https://docs.python.org/3/library/socketserver.html
# In this example, the minimal TCP server will send the binary file to a specified client on request.
# The client initiates the connection and sends a request message, followed by processing the server’s response message.
# The server waits for a connection, processes the client’s request message, and then sends a response message


if __name__ == '__main__':
    server.BinaryFTPServer()
    client.FILE = 'test.png'
    client.SimpleFTPClient()
