#!/usr/bin/env python3

import pika
import logging
from constants import HOST, END, CLOSE, OK, MATCHES_EXCHANGE

SURFACES = ['Hard', 'Clay', 'Carpet', 'Grass']
END_ENCODED = END.encode()
CLOSE_ENCODED = CLOSE.encode()
SURFACE_EXCHANGE = 'surfaces'
MATCHES_QUEUE = 'matches_surface'
TERMINATOR_EXCHANGE = 'dispatcher_terminator'

class SurfaceDispatcher:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange=SURFACE_EXCHANGE, exchange_type='direct')
        self.channel.exchange_declare(exchange=TERMINATOR_EXCHANGE, exchange_type='fanout')

        self.channel.exchange_declare(exchange=MATCHES_EXCHANGE, exchange_type='fanout')
        self.channel.queue_declare(queue=MATCHES_QUEUE, durable=True)
        self.channel.queue_bind(exchange=MATCHES_EXCHANGE, queue=MATCHES_QUEUE)

    def run(self):
        self.tag = self.channel.basic_consume(queue=MATCHES_QUEUE, auto_ack=True, on_message_callback=self.dispatch)
        self.channel.start_consuming()

    def dispatch(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == END_ENCODED:
            self.channel.basic_publish(exchange=TERMINATOR_EXCHANGE, routing_key='', body=END,
                                       properties=pika.BasicProperties(delivery_mode=2,))
            return

        if body == CLOSE_ENCODED:
            self.channel.basic_publish(exchange=TERMINATOR_EXCHANGE, routing_key='', body=OK,
                                       properties=pika.BasicProperties(delivery_mode=2,))
            self.channel.basic_cancel(self.tag)
            return

        data = body.decode().split(',')
        surface = data[3]
        minutes = data[9]

        if minutes == '' or surface in ('', 'None'):
            return

        self.channel.basic_publish(exchange=SURFACE_EXCHANGE, routing_key=surface, body=minutes)
        logging.info('Sent %s minutes to %s accumulator' % (minutes, surface))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)
    dispatcher = SurfaceDispatcher()
    dispatcher.run()
