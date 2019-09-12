#!/usr/bin/env python3

import sys, getopt, socket

def start():
    query, address = parse_args(sys.argv[1:])
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('master', 8080))
    client.send((query + ' ' + address).encode())

    response = client.recv(4096).decode()
    print(response)
    client.send("END".encode())
    client.close()

def parse_args(argv):
    try:
        options, args = getopt.getopt(argv,"a:r:",["analyze=", "report="])
    except getopt.GetoptError:
        print("Usage: 'client.py --analyze=address' or 'client.py --report=address'")
        sys.exit(2)

    for option, arg in options:
        if option in ("-a", "--analyze"):
            return "analyze", arg
        if option in ("-r", "--report"):
            return "report", arg

if __name__ == "__main__":
    start()
