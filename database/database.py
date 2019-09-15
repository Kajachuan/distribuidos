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

    manager = mp.Manager()
    persist_queue = mp.Queue()
    query_queue = mp.Queue()

    mp.Pool(1, resolve_query, (query_queue,))
    mp.Pool(1, persist, (persist_queue,))

    persistor_receiver = mp.Process(target=receive, args=(workers, persist_queue,))
    resolver_receiver = mp.Process(target=receive, args=(server, query_queue,))

    persistor_receiver.start()
    resolver_receiver.start()

    persistor_receiver.join()
    resolver_receiver.join()

def resolve_query(queries):
    while True:
        request, conn = queries.get()
        [id, address, path] = request.split()
        # Resolver query
        conn.sendall(('Query resuelta: ' + address).encode())
        conn.close()

def persist(data):
    while True:
        info, conn = data.get()
        # [address, abs_path, size] = info.split()
        print('Recibí ' + info)

def receive(created_socket, queue):
    conn, address = created_socket.accept()

    while True:
        request = conn.recv(BUFF_SIZE).decode()
        queue.put((request, conn))

if __name__ == '__main__':
    start()
