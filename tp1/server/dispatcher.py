#!/usr/bin/env python3

import multiprocessing as mp

BUFF_SIZE = 8192

class DispatcherPool:
    def __init__(self, processes, requests, to_analyze, to_query):
        self.requests = requests
        self.to_analyze = to_analyze
        self.to_query = to_query
        mp.Pool(processes, self.run)

    def run(self):
        while True:
            request, conn = self.requests.get()

            try:
                [request, address, path] = request.split()
            except ValueError:
                [request, address] = request.split()
                path = '/'

            if request == 'analyze':
                path = '/'
                conn.close()
                self.to_analyze.put((address, path))
            else:
                self.to_query.put((address, path, conn))
