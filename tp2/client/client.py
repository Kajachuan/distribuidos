#!/usr/bin/env python3

import pika
import logging
from glob import glob

class Client:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        logging.info('Connection created')

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='lines')
        logging.info('Queue "lines" created')

    def run(self):
        for filename in glob('./data/atp_matches_*.csv'):
            with open(filename, 'r') as file:
                file.readline()
                for line in iter(file.readline, ''):
                    self.channel.basic_publish(exchange='', routing_key='lines', body=line)
                    logging.debug('Sent: %s' % line)

    def __del__(self):
        self.connection.close()
        logging.info('Connection closed')

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    client = Client()
    client.run()
