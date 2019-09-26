#!/usr/bin/env python3

import multiprocessing as mp

BUFF_SIZE = 8192

class ResponsorPool:
    def __init__(self, processes, queue, db_conn):
        self.queue = queue
        self.db_conn = db_conn
        mp.Pool(processes, self.run)

    def run(self):
        while True:
            address, path, conn = self.queue.get()
            self.db_conn.sendall((address + ' ' + path).encode())
            self.db_conn.recv(BUFF_SIZE).decode()
            response = self.db_conn.recv(BUFF_SIZE).decode()
            conn.sendall(response.encode())
            conn.close()
