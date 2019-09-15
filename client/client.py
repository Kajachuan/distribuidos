#!/usr/bin/env python3

import sys, getopt, socket

BUFF_SIZE = 8192

def start():
    request = parse_args(sys.argv[1:])
    client = socket.create_connection(('server', 8080))
    client.sendall(request.encode())

    response = client.recv(BUFF_SIZE).decode()
    print(response)
    if response.split()[0] == 'report':
        response = client.recv(BUFF_SIZE).decode()
        print(response)
    client.close()

def parse_args(argv):
    try:
        options, args = getopt.getopt(argv,"a:r:p:",["analyze=", "report=", "path="])
    except getopt.GetoptError:
        print("Usage: 'client.py --analyze=address --path=path' or 'client.py --report=address --path=path'")
        sys.exit(2)

    request = ""
    for option, arg in options:
        if option in ("-a", "--analyze"):
            request = "analyze " + arg
        elif option in ("-r", "--report"):
            request = "report " + arg
        if option in ("-p", "--path"):
            request += " " + arg

    return request

if __name__ == '__main__':
    start()
