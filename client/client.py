#!/usr/bin/env python3

import sys, getopt, socket

BUFF_SIZE = 8192

class Client:
    def __init__(self, argv):
        self.request = self.parse_args(argv)

    def run(self):
        conn = socket.create_connection(('server', 8080))
        conn.sendall(self.request.encode())

        response = conn.recv(BUFF_SIZE).decode()
        print(response)
        if 'report' in self.request:
            response = conn.recv(BUFF_SIZE).decode()
            print(response)
        conn.close()

    def parse_args(self, argv):
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
    client = Client(sys.argv[1:])
    client.run()
