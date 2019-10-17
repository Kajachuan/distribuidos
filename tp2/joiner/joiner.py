#!/usr/bin/env python3

import pika
import logging
from glob import glob

class Joiner:
    def __init__(self):
        self.players = {}

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='matches_join', durable=True)
        self.channel.queue_declare(queue='joined_hands', durable=True)
        self.channel.queue_declare(queue='joined_age', durable=True)

        self.channel.exchange_declare(exchange='players', exchange_type='fanout')

        result = self.channel.queue_declare(queue='', exclusive=True, durable=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange='players', queue=queue_name)

        self.tag = self.channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=self.save_player)
        self.channel.start_consuming()

        self.tag = self.channel.basic_consume(queue='matches_join', auto_ack=True, on_message_callback=self.join)
        self.channel.start_consuming()

    def save_player(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == b'END':
            self.channel.basic_cancel(self.tag)
            return

        data = body.decode().split(',')
        self.players[data[0]] = data[1:5]

    def join(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == b'END':
            self.channel.basic_publish(exchange='', routing_key='joined_hands', body='END',
                                       properties=pika.BasicProperties(delivery_mode=2,))
            self.channel.basic_publish(exchange='', routing_key='joined_age', body='END',
                                       properties=pika.BasicProperties(delivery_mode=2,))
            self.channel.basic_cancel(self.tag)
            return

        data = body.decode().split(',')
        winner_id = data[4]
        loser_id = data[5]
        data = [data[2]] + self.players[winner_id] + self.players[loser_id]
        body = ','.join(data)
        self.channel.basic_publish(exchange='', routing_key='joined_hands', body=body,
                                   properties=pika.BasicProperties(delivery_mode=2,))
        self.channel.basic_publish(exchange='', routing_key='joined_age', body=body,
                                   properties=pika.BasicProperties(delivery_mode=2,))
        logging.info('Sent %s' % body)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)
    joiner = Joiner()
