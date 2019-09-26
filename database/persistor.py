#!/usr/bin/env python3

import multiprocessing as mp
import os

class PersistorPool:
    def __init__(self, processes, queue):
        self.queue = queue
        mp.Pool(processes, self.run)

    def run(self):
        while True:
            info, conn = self.queue.get()

            dirs = info.split('\n')
            for i in range(0, len(dirs) - 1):
                [type, address, abs_path, size] = dirs[i].split()

                if type == 'f':
                    dirname = '/database/' + address + os.path.dirname(abs_path)
                    filename = dirname + '/' + os.path.basename(abs_path)
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)
                    file = open(filename, 'w+')
                else:
                    dirname = '/database/' + address + abs_path
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)
                    file = open(dirname + '/.MY_SIZE', 'w+')

                file.write(size)
                file.close()
