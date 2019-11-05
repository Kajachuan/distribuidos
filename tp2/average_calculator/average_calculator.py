#!/usr/bin/env python3

import pika
import logging
from constants import HOST, END, DATABASE_EXCHANGE

AVERAGE_CALCULATOR_QUEUE = 'surface_values'
ROUTING_KEY = 'surface'

class AverageCalculator:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
        self.count = 0
        self.channel = connection.channel()
        self.channel.queue_declare(queue=AVERAGE_CALCULATOR_QUEUE, durable=True)

        self.channel.exchange_declare(exchange=DATABASE_EXCHANGE, exchange_type='direct')

    def run(self):
        self.tag = self.channel.basic_consume(queue=AVERAGE_CALCULATOR_QUEUE, auto_ack=True,
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
