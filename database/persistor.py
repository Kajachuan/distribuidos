#!/usr/bin/env python3

import multiprocessing as mp
import fcntl
import os

class PersistorPool:
    def __init__(self, processes, queue):
        self.queue = queue
        self.lock = mp.Manager().Lock()
        mp.Pool(processes, self.run)

    def run(self):
        while True:
            info, conn = self.queue.get()

            dirs = info.split('\n')
            for i in range(0, len(dirs) - 1):
                [type, address, abs_path, size] = dirs[i].split()

                if type == 'f':
                    self.persist_file(address, abs_path, size)

                self.update_sizes(address, abs_path, size, type)

    def update_sizes(self, address, path, size, type):
        if type == 'f':
            dir = os.path.dirname(path)
        else:
            dir = path

        while True:
            dirname = '/database/' + address + dir + ('' if dir == '/' else '/')
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            filename = dirname + '.MY_SIZE'
            self.lock.acquire()
            if not os.path.exists(filename):
                file = open(filename, 'w+')
                fcntl.lockf(file, fcntl.LOCK_EX)
                file.write(size)
                fcntl.lockf(file, fcntl.LOCK_UN)
                file.close()
            else:
                file = open(filename, 'r')
                fcntl.lockf(file, fcntl.LOCK_SH)
                dir_size = int(file.read())
                fcntl.lockf(file, fcntl.LOCK_UN)
                file.close()

                file = open(filename, 'w')
                fcntl.lockf(file, fcntl.LOCK_EX)
                file.write(str(dir_size + int(size)))
                fcntl.lockf(file, fcntl.LOCK_UN)
                file.close()
            self.lock.release()

            if dir == '/':
                return
            dir = os.path.dirname(dir)

    def persist_file(self, address, path, size):
        dirname = '/database/' + address + os.path.dirname(path)
        filename = dirname + '/' + os.path.basename(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        file = open(filename, 'w+')
        fcntl.lockf(file, fcntl.LOCK_EX)
        file.write(size)
        fcntl.lockf(file, fcntl.LOCK_UN)
        file.close()
