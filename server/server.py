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
    sessions = manager.dict()
    remaining = manager.dict()

    workers_pool = mp.Pool(5, analyze, (to_analyze, sessions, remaining, db_workers,))
    dispatchers_pool = mp.Pool(3, dispatch, (requests, to_analyze, to_query, db_dispatcher, connections,))

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
            response = database.recv(BUFF_SIZE).decode()
            conn = connections.get()
            conn.sendall(response.encode())
            conn.close()

def analyze(to_analyze, sessions, remaining, database):
    while True:
        id, address, path = to_analyze.get()

        if not (address, mp.current_process().name) in sessions:
            control, data = connect_to_server(address, sessions)
        else:
            control, data = sessions[(address, mp.current_process().name)]

        control.sendall(('LIST ' + path + '\r\n').encode())
        resp = control.recv(BUFF_SIZE).decode()
        print(resp)

        list = data.recv(BUFF_SIZE).decode()
        remaining[address] = remaining.get(address, 1) - 1
        parse_list_and_send(list, to_analyze, path, address, remaining, database)

        if remaining[address] == 0:
            for key, session in sessions[address].items():
                session[0].close()
                session[1].close()

def connect_to_server(address, sessions):
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
    sessions[(address, mp.current_process().name)] = (control, data)

    return control, data

def parse_list_and_send(list, to_analyze, path, address, remaining, database):
    list = list.split('\n')
    for i in range(0, len(list) - 1):
        data = list[i].split()
        abs_path = '/'.join(['' if path == '/' else path, data[8]])

        if data[0][0] == 'd':
            remaining[address] += 1
            id = str(uuid.uuid1())
            to_analyze.put((id, address, abs_path))
        else:
            pass
            # database.sendall((address + ' ' + abs_path + ' ' + data[4]).encode())

if __name__ == '__main__':
    start()
