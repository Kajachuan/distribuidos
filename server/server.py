#!/usr/bin/env python3

import socket
import multiprocessing as mp
import uuid

def receive(requests):
    master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master.bind(('', 8080))
    master.listen(5)

    while True:
        conn, address = master.accept()

        request = conn.recv(4096).decode()
        id = str(uuid.uuid1())
        requests.put((id, request))
        conn.sendall((request + ' received. ID: ' + id).encode())
        conn.close()

def dispatch(requests, to_analyze, to_query):
    while True:
        id, request = requests.get()

        try:
            [request, address, path] = request.split()
        except ValueError:
            [request, address] = request.split()
            path = '/'

        if request == 'analyze':
            to_analyze.put((id, address, path))
        else:
            print('Mandar a reporte ' + address + ' Path: ' + path + '. ID: ' + id)

def analyze(to_analyze):
    while True:
        id, address, path = to_analyze.get()

        control = socket.create_connection((address, 21))
        resp = control.recv(4096).decode()
        print(resp)
        control.sendall(b'USER username\r\n')
        resp = control.recv(4096).decode()
        print(resp)
        control.sendall(b'PASS mypass\r\n')
        resp = control.recv(4096).decode()
        print(resp)
        control.sendall(b'PASV\r\n')
        resp = control.recv(4096).decode()
        print(resp)
        info = resp.split('(')[1].split(')')[0].split(',')
        port = int(info[4]) * 256 + int(info[5])

        data = socket.create_connection((address, port))
        control.sendall(b'LIST /\r\n')
        resp = control.recv(4096).decode()
        print(resp)
        list = data.recv(4096).decode()
        print(list)

        data.close()
        control.close()

if __name__ == '__main__':
    requests = mp.Queue()
    to_analyze = mp.Queue()
    to_query = mp.Queue()

    worker = mp.Process(target=analyze, args=(to_analyze,))
    worker.start()

    dispatcher = mp.Process(target=dispatch, args=(requests, to_analyze, to_query,))
    dispatcher.start()

    receiver = mp.Process(target=receive, args=(requests,))
    receiver.start()
