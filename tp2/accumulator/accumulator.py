#!/usr/bin/env python3

import os
import pika
import logging

class Accumulator:
    def __init__(self, routing_key):
        self.amount = 0.0
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange='surfaces', exchange_type='direct')
        self.channel.queue_declare(queue='surfaces', exclusive=True)

        self.channel.queue_bind(exchange='surfaces', queue='surfaces', routing_key=routing_key)
        self.channel.basic_consume(queue='surfaces', auto_ack=True, on_message_callback=self.add)

        self.channel.start_consuming()

    def add(self, ch, method, properties, body):
        logging.info('[%s accumulator] Received %r' % (method.routing_key, body))
        self.amount += float(body.decode())

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)

    routing_key = os.environ['ROUTING_KEY']
    accumulator = Accumulator(routing_key)
