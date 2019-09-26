#!/usr/bin/env python3

import multiprocessing as mp
import os

class ResolverPool:
    def __init__(self, processes, queue):
        self.queue = queue
        mp.Pool(processes, self.run)

    def run(self):
        while True:
            request, conn = self.queue.get()
            [address, path] = request.split()
            abs_path = '/database/' + address + path + ('' if path[-1] == '/' else '/')
            try:
                files = sorted(os.listdir(abs_path))

                header = path + ': '
                total_size = 0
                inside = ''

                for i in range(0 if path == '/' else 1, len(files)):
                    try:
                        file = open(abs_path + files[i], 'r')
                    except IsADirectoryError:
                        file = open(abs_path + files[i] + '/.MY_SIZE', 'r')

                    size = file.read()
                    file.close()
                    total_size += int(size)
                    inside += '\t' + files[i] + ': ' + size + 'B\n'

                if path == '/':
                    total_size += 4096
                else:
                    file = open(abs_path + '/.MY_SIZE', 'r')
                    size = file.read()
                    file.close()
                    total_size += int(size)

                result = header + str(total_size) + 'B\n' + inside

            except FileNotFoundError:
                result = 'Report of' + address + ' does not exist'

            conn.sendall(result.encode())
            conn.close()
