#!/usr/bin/env python3

import socket
import multiprocessing as mp
import uuid

BUFF_SIZE = 8192

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('server', 8080))
    server.listen(5) # Max Clients

    db_dispatcher = socket.create_connection(('database', 8081))
    db_workers = socket.create_connection(('database', 8082))

    manager = mp.Manager()
    requests = manager.Queue()
    to_analyze = manager.Queue()
    to_query = manager.Queue()
    connections = manager.Queue()

    workers_pool = mp.Pool(1, analyze, (to_analyze, db_workers,))
    dispatchers_pool = mp.Pool(1, dispatch, (requests, to_analyze, to_query, db_dispatcher, connections,))

    receiver = mp.Process(target=receive, args=(requests, server, connections,))
    receiver.start()
    receiver.join()

def receive(requests, server, connections):
    while True:
        conn, address = server.accept()

        request = conn.recv(BUFF_SIZE).decode()
        id = str(uuid.uuid1())
        requests.put((id, request))
        conn.sendall((request + ' received. ID: ' + id).encode())
        if request.split()[0] == 'report':
            connections.put(conn)
        else:
            conn.close()

def dispatch(requests, to_analyze, to_query, database, connections):
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
            database.sendall((id + ' ' + address + ' ' + path).encode())
            database.recv(BUFF_SIZE).decode()
            response = database.recv(BUFF_SIZE).decode()
            conn = connections.get()
            conn.sendall(response.encode())
            conn.close()

def analyze(to_analyze, database):
    while True:
        id, address, path = to_analyze.get()

        control, data = connect_to_server(address)

        control.sendall(('LIST ' + path + '\r\n').encode())
        resp = control.recv(BUFF_SIZE).decode()
        print(resp)

        list = data.recv(BUFF_SIZE).decode()
        parse_list_and_send(list, to_analyze, path, address, database)

        control.sendall(b'QUIT\r\n')
        resp = control.recv(BUFF_SIZE).decode()
        print(resp)
        control.close()
        data.close()

def connect_to_server(address):
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

def parse_list_and_send(list, to_analyze, path, address, database):
    list = list.split('\n')
    for i in range(0, len(list) - 1):
        data = list[i].split()
        abs_path = '/'.join(['' if path == '/' else path, data[8]])
        if data[0][0] == 'd':
            id = str(uuid.uuid1())
            to_analyze.put((id, address, abs_path))
        else:
            database.sendall((address + ' ' + abs_path + ' ' + data[4] + '\n').encode())
            database.recv(BUFF_SIZE).decode()

if __name__ == '__main__':
    start()
