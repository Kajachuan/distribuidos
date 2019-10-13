#!/usr/bin/env python3

import pika
import logging
from glob import glob
import time

class Client:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        logging.info('Connection created')

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='lines', exchange_type='fanout')
        logging.info('Queue "lines" created')

    def run(self):
        for filename in glob('./data/atp_matches_*.csv'):
            with open(filename, 'r') as file:
                file.readline()
                for line in iter(file.readline, ''):
                    self.channel.basic_publish(exchange='lines', routing_key='', body=line)
                    logging.info('Sent %s' % line)

        self.channel.basic_publish(exchange='lines', routing_key='', body='EOF')

if __name__ == '__main__':
    time.sleep(20) # Revisar esto
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    client = Client()
    client.run()
