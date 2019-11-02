#!/usr/bin/env python3

import pika
import logging

HANDS = ['R', 'L', 'U']

class DifferentHandsFilter:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange='joined', exchange_type='fanout')
        self.channel.queue_declare(queue='joined_hands', durable=True)
        self.channel.queue_bind(exchange='joined', queue='joined_hands')

        self.channel.exchange_declare(exchange='hands', exchange_type='direct')

        self.channel.queue_declare(queue='hands_filter_terminator', durable=True)

        self.tag = self.channel.basic_consume(queue='joined_hands', auto_ack=True, on_message_callback=self.filter)
        self.channel.start_consuming()

    def filter(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == b'END':
            self.channel.basic_publish(exchange='', routing_key='hands_filter_terminator', body='END',
                                       properties=pika.BasicProperties(delivery_mode=2,))
            return

        if body == b'CLOSE':
            self.channel.basic_cancel(self.tag)
            return

        data = body.decode().split(',')
        winner_hand = data[3]
        loser_hand = data[7]
        if winner_hand in HANDS and loser_hand != winner_hand:
            self.channel.basic_publish(exchange='hands', routing_key=winner_hand, body='1')
            logging.info('Sent 1 to %s accumulator' % winner_hand)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)

    filter = DifferentHandsFilter()
