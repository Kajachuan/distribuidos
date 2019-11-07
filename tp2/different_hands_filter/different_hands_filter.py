#!/usr/bin/env python3

import pika
import logging
from constants import HOST, END, CLOSE, OK, OUT_JOINER_EXCHANGE

END_ENCODED = END.encode()
CLOSE_ENCODED = CLOSE.encode()
JOINED_QUEUE = 'joined_hands'
HANDS_EXCHANGE = 'hands'
TERMINATOR_EXCHANGE = 'hands_filter_terminator'

HANDS = ['R', 'L', 'U']

class DifferentHandsFilter:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange=OUT_JOINER_EXCHANGE, exchange_type='fanout')
        self.channel.queue_declare(queue=JOINED_QUEUE, durable=True)
        self.channel.queue_bind(exchange=OUT_JOINER_EXCHANGE, queue=JOINED_QUEUE)

        self.channel.exchange_declare(exchange=HANDS_EXCHANGE, exchange_type='direct')
        self.channel.exchange_declare(exchange=TERMINATOR_EXCHANGE, exchange_type='fanout')

    def run(self):
        self.tag = self.channel.basic_consume(queue=JOINED_QUEUE, auto_ack=True, on_message_callback=self.filter)
        self.channel.start_consuming()

    def filter(self, ch, method, properties, body):
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
        winner_hand = data[3]
        loser_hand = data[7]
        if winner_hand in HANDS and loser_hand != winner_hand:
            self.channel.basic_publish(exchange=HANDS_EXCHANGE, routing_key=winner_hand, body='1')
            logging.info('Sent 1 to %s accumulator' % winner_hand)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)

    filter = DifferentHandsFilter()
    filter.run()
