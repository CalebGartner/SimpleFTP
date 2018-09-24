#!/usr/bin/env python3
# TODO calculate checksum at beginning and end to verify integrity


# uses TCP by default, uses binary encoding by default
import socket

HOST = 'local_host'
PORT = 9528
BUFFER_SIZE = 512  # bytes


class SimpleServer:  # not really a server, just a listener on a port

    @staticmethod
    def startup(file_name: str):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s, open('file_destination/' + file_name + '_copy', 'w+b') as file_copy:
                s.bind((HOST, PORT))
                s.listen()
                print('listening . . .')
                client, addr = s.accept()
                with client:
                    print(f'Client connection from {addr}')
                    while True:
                        data = client.recv(BUFFER_SIZE)
                        if not data: break
                        file_copy.write(data)

        except Exception as err:  # oof ouch
            print(f"server: start: error: {err}")

