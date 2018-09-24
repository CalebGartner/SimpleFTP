#!/usr/bin/env python3
import simple_server
import simple_client

# generate binary file with: 'dd if=/dev/urandom of=4GB.bin bs=64M count=64 iflag=fullblock'
FILE = '4GB.bin'


def main():
    server = simple_server.SimpleServer()
    client = simple_client.Client()

    server.startup(FILE)
    client.startup(FILE)


if __name__ == '__main__':
    main()