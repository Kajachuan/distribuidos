#!/usr/bin/env python3

import pika
import logging
from glob import glob

class Client:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='lines_join', durable=True)
        self.channel.queue_declare(queue='lines_surface', durable=True)
        self.channel.queue_declare(queue='response', durable=True)

    def run(self):
        for filename in glob('./data/atp_matches_*.csv'): # Cambiar 2017 por * despues
            with open(filename, 'r') as file:
                file.readline()
                for line in iter(file.readline, ''):
                    self.channel.basic_publish(exchange='', routing_key='lines_join', body=line,
                                               properties=pika.BasicProperties(delivery_mode=2,))
                    self.channel.basic_publish(exchange='', routing_key='lines_surface', body=line,
                                               properties=pika.BasicProperties(delivery_mode=2,))
                    logging.info('Sent %s' % line)

        self.channel.basic_publish(exchange='', routing_key='lines_join', body='END',
                                   properties=pika.BasicProperties(delivery_mode=2,))
        self.channel.basic_publish(exchange='', routing_key='lines_surface', body='END',
                                   properties=pika.BasicProperties(delivery_mode=2,))

        self.channel.basic_consume(queue='response', auto_ack=True, on_message_callback=self.print_response)
        self.channel.start_consuming()

    def print_response(self, ch, method, properties, body):
        print(body.decode())

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    client = Client()
    client.run()
