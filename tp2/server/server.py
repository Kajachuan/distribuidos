#!/usr/bin/env python3

import pika
import logging
from surface_dispatcher import SurfaceDispatcher

class Server:
    def __init__(self):
        surface = SurfaceDispatcher()
        surface.run()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    server = Server()
