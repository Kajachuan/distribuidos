#!/usr/bin/env python3

import pika
import logging

class DifferentHandsFilter:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange='joined', exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange='joined', queue=queue_name)

        self.tag = self.channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=self.filter)
        self.channel.start_consuming()

    def filter(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        data = body.decode().split(',')
        winner_hand = data[3]
        loser_hand = data[7]
        if winner_hand in ('R', 'L', 'U') and loser_hand != winner_hand:
            data = ','.join([winner_hand, loser_hand])
            logging.info('Sent %s' % data)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)

    filter = DifferentHandsFilter()
