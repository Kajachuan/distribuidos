#!/usr/bin/env python3

import socket

FTP_PORT = 21
BUFF_SIZE = 8192

class FTPClient:
    def __init__(self, address):
        self.data = None
        self.control = socket.create_connection((address, FTP_PORT))
        self.address = address
        resp = self.control.recv(BUFF_SIZE).decode()
        print(resp)

    def login(self, username, password):
        self.control.sendall(('USER ' + username + '\r\n').encode())
        resp = self.control.recv(BUFF_SIZE).decode()
        print(resp)
        self.control.sendall(('PASS ' + password + '\r\n').encode())
        resp = self.control.recv(BUFF_SIZE).decode()
        print(resp)

    def create_data_connection(self):
        self.control.sendall(b'PASV\r\n')
        resp = self.control.recv(BUFF_SIZE).decode()
        print(resp)
        info = resp.split('(')[1].split(')')[0].split(',')
        port = int(info[4]) * 256 + int(info[5])

        self.data = socket.create_connection((self.address, port))

    def list(self, path):
        self.control.sendall(('LIST ' + path + '\r\n').encode())
        resp = self.control.recv(BUFF_SIZE).decode()
        print(resp)

        list = self.data.recv(BUFF_SIZE).decode()
        return list

    def quit(self):
        self.control.sendall(b'QUIT\r\n')
        resp = self.control.recv(BUFF_SIZE).decode()
        print(resp)
        self.control.close()
        self.data.close()
