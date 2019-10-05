#!/usr/bin/env python3

import multiprocessing as mp
import fcntl
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

                result = 'Status: '
                status = 0
                if not os.path.exists('/database/' + address + '/.FINISH'):
                    result += 'In Progress\n'
                else:
                    status = 1
                    result += 'Finished\n'

                result += path + ': '
                file = open(abs_path + '/.MY_SIZE', 'r')
                fcntl.lockf(file, fcntl.LOCK_SH)
                size = file.read()
                fcntl.lockf(file, fcntl.LOCK_UN)
                file.close()
                result += size + 'B\n'

                for i in range(1 + status if path == '/' else 1, len(files)):
                    try:
                        file = open(abs_path + files[i], 'r')
                    except IsADirectoryError:
                        file = open(abs_path + files[i] + '/.MY_SIZE', 'r')

                    fcntl.lockf(file, fcntl.LOCK_SH)
                    size = file.read()
                    fcntl.lockf(file, fcntl.LOCK_UN)
                    file.close()
                    result += '\t' + files[i] + ': ' + size + 'B\n'

            except FileNotFoundError:
                result = 'Report of ' + address + ' does not exist'

            conn.sendall(result.encode())
            conn.close()
