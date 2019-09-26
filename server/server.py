#!/usr/bin/env python3

import socket
import multiprocessing as mp
import uuid
import os
from analyzer import AnalyzerPool
from dispatcher import DispatcherPool

BUFF_SIZE = 8192
MAX_CLIENTS_DEFAULT = 5
WORKERS_NUMBER_DEFAULT = 3
DISPATCHERS_NUMBER_DEFAULT = 3

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('server', 8080))
        self.server.listen(int(os.getenv('MAX_CLIENTS', MAX_CLIENTS_DEFAULT)))

        self.db_dispatcher = socket.create_connection(('database', 8081))
        self.db_analyzers = socket.create_connection(('database', 8082))

        manager = mp.Manager()
        self.requests = manager.Queue()
        self.to_analyze = manager.Queue()
        self.to_query = manager.Queue()
        self.connections = manager.Queue()

    def run(self):
        analyzers = AnalyzerPool(int(os.getenv('WORKERS_NUMBER', WORKERS_NUMBER_DEFAULT)),
                                 self.to_analyze, self.db_analyzers)

        dispatchers = DispatcherPool(int(os.getenv('DISPATCHERS_NUMBER', DISPATCHERS_NUMBER_DEFAULT)),
                                     self.requests, self.to_analyze, self.to_query, self.db_dispatcher, self.connections)

        receiver = mp.Process(target=self.receive_requests)
        receiver.start()
        receiver.join()

    def receive_requests(self):
        while True:
            conn, address = self.server.accept()

            request = conn.recv(BUFF_SIZE).decode()
            id = str(uuid.uuid1())
            self.requests.put((id, request))
            conn.sendall((request + ' received. ID: ' + id).encode())
            if request.split()[0] == 'report':
                self.connections.put(conn)
            else:
                conn.close()

if __name__ == '__main__':
    server = Server()
    server.run()
