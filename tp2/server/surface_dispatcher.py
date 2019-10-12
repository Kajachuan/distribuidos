#!/usr/bin/env python3

import pika
import logging

class SurfaceDispatcher:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        logging.info('Connection created')

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='lines')
        logging.info('Queue "lines" created')

        self.channel.basic_consume(queue='lines', auto_ack=True, on_message_callback=self.dispatch)

    def run(self):
        self.channel.start_consuming()

    def dispatch(self, ch, method, properties, body):
        logging.debug('Received: %r' % body)
        data = str(body).split(',')
        surface = data[3]
        minutes = 0 if data[9] == '' else float(data[9])
        logging.info('%s: %f' % (surface, minutes))
