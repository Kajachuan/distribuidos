#!/usr/bin/env python3

import pika
import logging
from constants import HOST, END, DATABASE_EXCHANGE

ROUTING_KEY = 'hand'
RIGHT = 'R'
NO_RIGHT = 'L-U'
HANDS_QUEUE = 'hands_values'

class PercentageCalculator:
    def __init__(self):
        self.left = None
        self.right = None
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
        self.channel = connection.channel()
        self.channel.queue_declare(queue=HANDS_QUEUE, durable=True)

        self.channel.exchange_declare(exchange=DATABASE_EXCHANGE, exchange_type='direct')

    def run(self):
        self.tag = self.channel.basic_consume(queue=HANDS_QUEUE, auto_ack=True, on_message_callback=self.calculate)
        self.channel.start_consuming()

    def calculate(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        [hand, amount, total] = body.decode().split(',')
        if hand == RIGHT:
            self.right = float(amount)
            if self.left is None:
                return

        if hand == NO_RIGHT:
            self.left = float(amount)
            if self.right is None:
                return

        right_percentage = 100 * self.right / (self.left + self.right)
        left_percentage = 100 - right_percentage
        right_response = 'R Victories: {}%'.format(right_percentage)
        left_response = 'L Victories: {}%'.format(left_percentage)
        self.channel.basic_publish(exchange=DATABASE_EXCHANGE, routing_key=ROUTING_KEY, body=right_response,
                                   properties=pika.BasicProperties(delivery_mode=2,))
        self.channel.basic_publish(exchange=DATABASE_EXCHANGE, routing_key=ROUTING_KEY, body=left_response,
                                   properties=pika.BasicProperties(delivery_mode=2,))
        self.channel.basic_publish(exchange=DATABASE_EXCHANGE, routing_key=ROUTING_KEY, body=END,
                                   properties=pika.BasicProperties(delivery_mode=2,))
        self.channel.basic_cancel(self.tag)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)

    calculator = PercentageCalculator()
    calculator.run()
