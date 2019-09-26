#!/usr/bin/env python3

import multiprocessing as mp

BUFF_SIZE = 8192

class DispatcherPool:
    def __init__(self, processes, requests, to_analyze, to_query, db_dispatcher, connections):
        self.requests = requests
        self.to_analyze = to_analyze
        self.to_query = to_query
        self.db_dispatcher = db_dispatcher
        self.connections = connections
        mp.Pool(processes, self.run)

    def run(self):
        while True:
            id, request = self.requests.get()

            try:
                [request, address, path] = request.split()
            except ValueError:
                [request, address] = request.split()
                path = '/'

            if request == 'analyze':
                path = '/'
                self.to_analyze.put((id, address, path))
            else:
                self.db_dispatcher.sendall((id + ' ' + address + ' ' + path).encode())
                self.db_dispatcher.recv(BUFF_SIZE).decode()
                response = self.db_dispatcher.recv(BUFF_SIZE).decode()
                conn = self.connections.get()
                conn.sendall(response.encode())
                conn.close()
