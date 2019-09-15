#!/usr/bin/env python3

import socket
import multiprocessing as mp

BUFF_SIZE = 8192

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('database', 8081))
    server.listen(3) # Dispatchers

    workers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    workers.bind(('database', 8082))
    workers.listen(5) # Workers

    persistor = mp.Process(target=persist, args=(workers,))
    resolver = mp.Process(target=resolve_query, args=(server,))

    persistor.start()
    resolver.start()

    persistor.join()
    resolver.join()

def resolve_query(workers):
    while True:
        conn, address = workers.accept()

        request = conn.recv(BUFF_SIZE).decode()
        [id, address, path] = request.split()
        # Resolver query
        conn.sendall(('Query resuelta: ' + address).encode())
        conn.close()

def persist(server):
    while True:
        conn, address = server.accept()
        conn.close()

if __name__ == '__main__':
    start()
