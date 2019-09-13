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
        ftp = socket.create_connection(('ftp_server', 21))
        resp = ftp.recv(4096).decode()
        print(resp)
        ftp.sendall(b'USER username\n')
        resp = ftp.recv(4096).decode()
        print(resp)
        ftp.sendall(b'PASS mypass\n')
        resp = ftp.recv(4096).decode()
        print(resp)
        ftp.close()

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
