#!/usr/bin/env python3

import server
import client

# TODO calculate checksum at beginning and end to verify integrity - send in header?
# TODO use jpg/png file instead
# TODO make host/port/file configurable

# Reference: https://realpython.com/python-sockets/
# In this example, the minimal TCP server will send the binary file to a specified client on request.
# The client initiates the connection and sends a request message, followed by processing the server’s response message.
# The server waits for a connection, processes the client’s request message, and then sends a response message
# Binary File Transfer Protocol:
#     TCP:
#         - in-order data and reliable transmission
#         - timeout/retries should be specified, and requesting specific chunks from the file may be supported
#     Header:
#         - total number of chunks in file
#         - specific chunk number (shouldn't be necessary since TCP sends data in order)
#         - should it send (x%) part of the calculated checksum?
#     Close:
#         - closing message for the server using the FTP should be specified


def main():
    pass


if __name__ == '__main__':
    main()