#!/usr/bin/env python3

import pika
import logging

class PercentageCalculator:
    def __init__(self):
        self.left = None
        self.right = None
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()
        self.channel.queue_declare(queue='hands_values', durable=True)

        self.channel.queue_declare(queue='database', durable=True)

        self.tag = self.channel.basic_consume(queue='hands_values', auto_ack=True, on_message_callback=self.calculate)
        self.channel.start_consuming()

    def calculate(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        [hand, amount, total] = body.decode().split(',')
        if hand == 'R':
            self.right = float(amount)
            if self.left is None:
                return

        if hand == 'L-U':
            self.left = float(amount)
            if self.right is None:
                return

        right_percentage = 100 * self.right / (self.left + self.right)
        left_percentage = 100 - right_percentage
        right_response = 'R Victories: {}%'.format(right_percentage)
        left_response = 'L Victories: {}%'.format(left_percentage)
        self.channel.basic_publish(exchange='', routing_key='database', body=','.join([right_response, 'hand']),
                                   properties=pika.BasicProperties(delivery_mode=2,))
        self.channel.basic_publish(exchange='', routing_key='database', body=','.join([left_response, 'hand']),
                                   properties=pika.BasicProperties(delivery_mode=2,))
        self.channel.basic_publish(exchange='', routing_key='database', body='END,hand',
                                   properties=pika.BasicProperties(delivery_mode=2,))
        self.channel.basic_cancel(self.tag)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)

    calculator = PercentageCalculator()
