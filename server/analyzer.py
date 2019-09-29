#!/usr/bin/env python3

import socket
import multiprocessing as mp
from ftp_client import FTPClient

BUFF_SIZE = 8192

class AnalyzerPool:
    def __init__(self, processes, queue):
        self.queue = queue
        self.db_conn = socket.create_connection(('database', 8082))
        self.remaining = mp.Manager().dict()
        mp.Pool(processes, self.run)

    def run(self):
        while True:
            address, path = self.queue.get()

            conn = FTPClient(address)
            conn.login('username', 'mypass')
            conn.create_data_connection()
            list = conn.list(path)
            conn.quit()
            self.parse_list_and_send(list, path, address)

    def parse_list_and_send(self, list, path, address):
        self.remaining[address] = self.remaining.get(address, 1) - 1
        list = list.split('\n')
        for i in range(0, len(list) - 1):
            data = list[i].split()
            abs_path = '/'.join(['' if path == '/' else path, data[8]])
            if data[0][0] == 'd':
                self.remaining[address] += 1
                self.queue.put((address, abs_path))
                self.db_conn.sendall(('d ' + address + ' ' + abs_path + ' ' + data[4] + '\n').encode())
            else:
                self.db_conn.sendall(('f ' + address + ' ' + abs_path + ' ' + data[4] + '\n').encode())

            self.db_conn.recv(BUFF_SIZE).decode()
