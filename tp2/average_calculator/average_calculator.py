#!/usr/bin/env python3

import pika
import logging
from constants import HOST, END, DATABASE_EXCHANGE

AVERAGE_CALCULATOR_EXCHANGE = 'surface_values'
ROUTING_KEY = 'surface'

class AverageCalculator:
    def __init__(self):
        self.count = 0

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange=AVERAGE_CALCULATOR_EXCHANGE, exchange_type='fanout')
        result = self.channel.queue_declare(queue='', durable=True, exclusive=True)
        self.queue_name = result.method.queue
        self.channel.queue_bind(exchange=AVERAGE_CALCULATOR_EXCHANGE, queue=self.queue_name)

        self.channel.exchange_declare(exchange=DATABASE_EXCHANGE, exchange_type='direct')

    def run(self):
        self.tag = self.channel.basic_consume(queue=self.queue_name, auto_ack=True,
                                              on_message_callback=self.calculate)
        self.channel.start_consuming()

    def calculate(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        [surface, amount, total] = body.decode().split(',')
        avg = float(total) / float(amount)
        result = '{}: {} minutes'.format(surface, avg)
        self.channel.basic_publish(exchange=DATABASE_EXCHANGE, routing_key=ROUTING_KEY, body=result,
                                   properties=pika.BasicProperties(delivery_mode=2,))
        self.count += 1
        if self.count == 3:
            self.channel.basic_publish(exchange=DATABASE_EXCHANGE, routing_key=ROUTING_KEY, body=END,
                                       properties=pika.BasicProperties(delivery_mode=2,))
            self.channel.basic_cancel(self.tag)
        logging.info('Sent %s' % result)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)

    calculator = AverageCalculator()
    calculator.run()
