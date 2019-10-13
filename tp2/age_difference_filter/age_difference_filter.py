#!/usr/bin/env python3

import pika
import logging

class AgeDifferenceFilter:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()
        self.channel.queue_declare(queue='surface_values')

        self.channel.exchange_declare(exchange='age', exchange_type='direct')
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange='age', queue=queue_name, routing_key='')
        self.tag = self.channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=self.filter)

        self.channel.start_consuming()

    def filter(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        data = body.decode().split(',')
        winner_age = int(data[4])
        loser_age = int(data[8])
        if winner_age - loser_age >= 20:
            winner_name = ' '.join([data[1], data[2]])
            loser_name = ' '.join([data[5], data[6]])
            logging.info('%d\t%s\t%d\t%s' % (winner_age, winner_name, loser_age, loser_name))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)

    filter = AgeDifferenceFilter()
