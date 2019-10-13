#!/usr/bin/env python3

import pika
import logging

SURFACES = ['Hard', 'Clay', 'Carpet', 'Grass']

class SurfaceDispatcher:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange='lines', exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange='lines', queue=queue_name)

        self.channel.exchange_declare(exchange='surfaces', exchange_type='direct')

        self.tag = self.channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=self.dispatch)
        self.channel.start_consuming()

    def dispatch(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == b'END':
            for surface in SURFACES:
                self.channel.basic_publish(exchange='surfaces', routing_key=surface, body='END')
            self.channel.basic_cancel(self.tag)
            return

        data = body.decode().split(',')
        surface = data[3]
        minutes = data[9]

        if minutes == '' or surface in ('', 'None'):
            return

        self.channel.basic_publish(exchange='surfaces', routing_key=surface, body=minutes)
        logging.info('Sent %s minutes to %s accumulator' % (minutes, surface))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    dispatcher = SurfaceDispatcher()
