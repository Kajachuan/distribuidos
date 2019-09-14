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
            path = '/'
            to_analyze.put((id, address, path))
        else:
            print('Mandar a reporte ' + address + ' Path: ' + path + '. ID: ' + id)

def analyze(to_analyze):
    while True:
        id, address, path = to_analyze.get()

        control, data = connect_to_server(address)

        control.sendall(('LIST ' + path + '\r\n').encode())
        resp = control.recv(4096).decode()
        print(resp)

        list = data.recv(4096).decode()
        parse_list_and_send(list, to_analyze, path, address)

        data.close()
        control.close()

def connect_to_server(address):
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
    return control, data

def parse_list_and_send(list, to_analyze, path, address):
    list = list.split('\n')
    for i in range(0, len(list) - 1):
        data = list[i].split()
        abs_path = '/'.join(['' if path == '/' else path, data[8]])

        if data[0][0] == 'd':
            print((abs_path, data[4]))
            id = str(uuid.uuid1())
            to_analyze.put((id, address, abs_path))
        else:
            pass
            # Enviar a database (abs_path, data[4])

if __name__ == '__main__':
    manager = mp.Manager()
    requests = manager.Queue()
    to_analyze = manager.Queue()
    to_query = manager.Queue()

    workers_pool = mp.Pool(5, analyze, (to_analyze,))
    workers_dispatchers = mp.Pool(3, dispatch, (requests, to_analyze, to_query,))

    receiver = mp.Process(target=receive, args=(requests,))
    receiver.start()
    receiver.join()
