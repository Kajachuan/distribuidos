#!/usr/bin/env python3

import os
import pika
import logging

class Accumulator:
    def __init__(self, routing_key, exchange, output_queue):
        self.routing_key = routing_key
        self.output_queue = output_queue
        self.total = 0
        self.amount = 0.0
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.queue_declare(queue=output_queue, durable=True)

        self.channel.exchange_declare(exchange=exchange, exchange_type='direct')
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        for surface in routing_key.split('-'):
            self.channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=surface)
        self.tag = self.channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=self.add)

        self.channel.start_consuming()

    def add(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == b'END':
            body = ','.join([self.routing_key, str(self.amount), str(self.total)])
            self.channel.basic_publish(exchange='', routing_key=self.output_queue, body=body,
                                       properties=pika.BasicProperties(delivery_mode=2,))
            self.channel.basic_cancel(self.tag)
            return

        self.total += float(body.decode())
        self.amount += 1
        logging.debug('Current total: %f' % self.total)
        logging.debug('Current amount: %f' % self.amount)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)

    routing_key = os.environ['ROUTING_KEY']
    exchange = os.environ['EXCHANGE']
    output_queue = os.environ['OUTPUT_QUEUE']
    accumulator = Accumulator(routing_key, exchange, output_queue)
