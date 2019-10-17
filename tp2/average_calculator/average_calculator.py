#!/usr/bin/env python3

import pika
import logging

class AverageCalculator:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.count = 0
        self.channel = connection.channel()
        self.channel.queue_declare(queue='surface_values', durable=True)

        self.channel.queue_declare(queue='database', durable=True)

        self.channel.basic_consume(queue='surface_values', auto_ack=True, on_message_callback=self.calculate)
        self.channel.start_consuming()

    def calculate(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        [surface, amount, total] = body.decode().split(',')
        avg = float(total) / float(amount)
        result = '{}: {} minutes'.format(surface, avg)
        self.channel.basic_publish(exchange='', routing_key='database', body=','.join([result, 'surface']),
                                   properties=pika.BasicProperties(delivery_mode=2,))
        self.count += 1
        if self.count == 3:
            self.channel.basic_publish(exchange='', routing_key='database', body='END,surface',
                                       properties=pika.BasicProperties(delivery_mode=2,))
        logging.info('Sent %s' % result)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)

    calculator = AverageCalculator()
