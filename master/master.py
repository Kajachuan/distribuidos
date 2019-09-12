#!/usr/bin/env python3

import socket

def start():
    master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master.bind(('', 8080))
    master.listen(5)

    while True:
        conn, address = master.accept()
        print(address)

        while True:
            data = conn.recv(4096).decode()
            if data == "END": break
            conn.send("Recibido".encode())

        conn.close()

if __name__ == "__main__":
    start()
