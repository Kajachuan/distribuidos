#!/usr/bin/env python3

import pika
import logging

SURFACES = ['Hard', 'Clay', 'Carpet', 'Grass']

class SurfaceDispatcher:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange='matches', exchange_type='fanout')
        self.channel.queue_declare(queue='matches_surface', durable=True)
        self.channel.queue_bind(exchange='matches', queue='matches_surface')

        self.channel.exchange_declare(exchange='surfaces', exchange_type='direct')

        self.channel.queue_declare(queue='dispatcher_terminator', durable=True)

        self.tag = self.channel.basic_consume(queue='matches_surface', auto_ack=True, on_message_callback=self.dispatch)
        self.channel.start_consuming()

    def dispatch(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == b'END':
            self.channel.basic_publish(exchange='', routing_key='dispatcher_terminator', body='END',
                                       properties=pika.BasicProperties(delivery_mode=2,))
            return

        if body == b'CLOSE':
            self.channel.basic_publish(exchange='', routing_key='dispatcher_terminator', body='OK',
                                       properties=pika.BasicProperties(delivery_mode=2,))
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
                        level=logging.ERROR)
    dispatcher = SurfaceDispatcher()
