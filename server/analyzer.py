#!/usr/bin/env python3

import socket
import multiprocessing as mp

BUFF_SIZE = 8192

class AnalyzerPool:
    def __init__(self, processes, queue, db_conn):
        self.queue = queue
        self.db_conn = db_conn
        mp.Pool(processes, self.run)

    def run(self):
        while True:
            address, path = self.queue.get()

            control, data = self.connect_to_ftp_server(address)

            control.sendall(('LIST ' + path + '\r\n').encode())
            resp = control.recv(BUFF_SIZE).decode()
            print(resp)

            list = data.recv(BUFF_SIZE).decode()
            self.parse_list_and_send(list, path, address)

            control.sendall(b'QUIT\r\n')
            resp = control.recv(BUFF_SIZE).decode()
            print(resp)
            control.close()
            data.close()

    def connect_to_ftp_server(self, address):
        control = socket.create_connection((address, 21))
        resp = control.recv(BUFF_SIZE).decode()
        print(resp)
        control.sendall(b'USER username\r\n')
        resp = control.recv(BUFF_SIZE).decode()
        print(resp)
        control.sendall(b'PASS mypass\r\n')
        resp = control.recv(BUFF_SIZE).decode()
        print(resp)
        control.sendall(b'PASV\r\n')
        resp = control.recv(BUFF_SIZE).decode()
        print(resp)
        info = resp.split('(')[1].split(')')[0].split(',')
        port = int(info[4]) * 256 + int(info[5])

        data = socket.create_connection((address, port))

        return control, data

    def parse_list_and_send(self, list, path, address):
        list = list.split('\n')
        for i in range(0, len(list) - 1):
            data = list[i].split()
            abs_path = '/'.join(['' if path == '/' else path, data[8]])
            if data[0][0] == 'd':
                self.queue.put((address, abs_path))
                self.db_conn.sendall(('d ' + address + ' ' + abs_path + ' ' + data[4] + '\n').encode())
            else:
                self.db_conn.sendall(('f ' + address + ' ' + abs_path + ' ' + data[4] + '\n').encode())

            self.db_conn.recv(BUFF_SIZE).decode()
