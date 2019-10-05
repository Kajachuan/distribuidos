#!/usr/bin/env python3

import socket
import multiprocessing as mp
import os
from persistor import PersistorPool
from resolver import ResolverPool

BUFF_SIZE = 8192
MAX_RESPONSORS_DEFAULT = 3
MAX_ANALYZERS_DEFAULT = 3
RESOLVERS_NUMBER_DEFAULT = 3
PERSISTORS_NUMBER_DEFAULT = 3

class Database:
    def __init__(self):
        self.responsor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.responsor.bind(('database', 8081))
        self.responsor.listen(int(os.getenv('MAX_RESPONSORS', MAX_RESPONSORS_DEFAULT)))

        self.analyzer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.analyzer.bind(('database', 8082))
        self.analyzer.listen(int(os.getenv('MAX_ANALYZERS', MAX_ANALYZERS_DEFAULT)))

        manager = mp.Manager()
        self.persist_queue = manager.Queue()
        self.query_queue = manager.Queue()

    def run(self):
        resolvers = ResolverPool(int(os.getenv('RESOLVERS_NUMBER', RESOLVERS_NUMBER_DEFAULT)), self.query_queue)
        persistors = PersistorPool(int(os.getenv('PERSISTORS_NUMBER', PERSISTORS_NUMBER_DEFAULT)), self.persist_queue)

        persistor_receiver = mp.Process(target=self.receive, args=(self.analyzer, self.persist_queue,))
        resolver_receiver = mp.Process(target=self.receive, args=(self.responsor, self.query_queue,))

        persistor_receiver.start()
        resolver_receiver.start()

        persistor_receiver.join()
        resolver_receiver.join()

    def receive(self, created_socket, queue):
        conn, address = created_socket.accept()

        while True:
            request = conn.recv(BUFF_SIZE).decode()
            queue.put((request, conn))
            conn.sendall(b'OK')

if __name__ == '__main__':
    db = Database()
    db.run()
