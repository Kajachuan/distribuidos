#!/usr/bin/env python3

import pika
import logging
from glob import glob

class Joiner:
    def __init__(self):
        self.players = {}
        with open('./data/atp_players.csv', 'r') as file:
            file.readline()
            for line in iter(file.readline, ''):
                data = line.split(',')
                self.players[data[0]] = data[1:5]

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='lines', exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange='lines', queue=queue_name)

        self.channel.queue_declare(queue='joined_hands', durable=True)
        self.channel.queue_declare(queue='joined_age', durable=True)

        self.tag = self.channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=self.join)
        self.channel.start_consuming()

    def join(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == b'END':
            self.channel.basic_publish(exchange='', routing_key='joined_hands', body='END')
            self.channel.basic_publish(exchange='', routing_key='joined_age', body='END')
            self.channel.basic_cancel(self.tag)
            return

        data = body.decode().split(',')
        winner_id = data[4]
        loser_id = data[5]
        data = [data[2]] + self.players[winner_id] + self.players[loser_id]
        body = ','.join(data)
        self.channel.basic_publish(exchange='', routing_key='joined_hands', body=body)
        self.channel.basic_publish(exchange='', routing_key='joined_age', body=body)
        logging.info('Sent %s' % body)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    joiner = Joiner()
