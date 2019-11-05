#!/usr/bin/env python3

import pika
import logging
from constants import HOST, END, CLOSE, OK, OUT_JOINER_EXCHANGE, \
                      MATCHES_EXCHANGE, PLAYERS_EXCHANGE

END_ENCODED = END.encode()
CLOSE_ENCODED = CLOSE.encode()
MATCHES_QUEUE = 'matches_join'
TERMINATOR_QUEUE = 'joiner_terminator'

class Joiner:
    def __init__(self):
        self.players = {}

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=MATCHES_EXCHANGE, exchange_type='fanout')
        self.channel.queue_declare(queue=MATCHES_QUEUE, durable=True)
        self.channel.queue_bind(exchange=MATCHES_EXCHANGE, queue=MATCHES_QUEUE)

        self.channel.queue_declare(queue=TERMINATOR_QUEUE, durable=True)

        self.channel.exchange_declare(exchange=OUT_JOINER_EXCHANGE, exchange_type='fanout')

        self.channel.exchange_declare(exchange=PLAYERS_EXCHANGE, exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True, durable=True)
        self.queue_name = result.method.queue
        self.channel.queue_bind(exchange=PLAYERS_EXCHANGE, queue=self.queue_name)

    def run(self):
        self.tag = self.channel.basic_consume(queue=self.queue_name, auto_ack=True, on_message_callback=self.save_player)
        self.channel.start_consuming()

        self.tag = self.channel.basic_consume(queue=MATCHES_QUEUE, auto_ack=True, on_message_callback=self.join)
        self.channel.start_consuming()

    def save_player(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == END_ENCODED:
            self.channel.basic_cancel(self.tag)
            return

        data = body.decode().split(',')
        self.players[data[0]] = data[1:5]

    def join(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == END_ENCODED:
            self.channel.basic_publish(exchange='', routing_key=TERMINATOR_QUEUE, body=END,
                                       properties=pika.BasicProperties(delivery_mode=2,))
            return

        if body == CLOSE_ENCODED:
            self.channel.basic_publish(exchange='', routing_key=TERMINATOR_QUEUE, body=OK,
                                       properties=pika.BasicProperties(delivery_mode=2,))
            self.channel.basic_cancel(self.tag)
            return

        data = body.decode().split(',')
        winner_id = data[4]
        loser_id = data[5]
        data = [data[2]] + self.players[winner_id] + self.players[loser_id]
        body = ','.join(data)
        self.channel.basic_publish(exchange=OUT_JOINER_EXCHANGE, routing_key='', body=body,
                                   properties=pika.BasicProperties(delivery_mode=2,))
        logging.info('Sent %s' % body)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)
    joiner = Joiner()
    joiner.run()
