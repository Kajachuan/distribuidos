#!/usr/bin/env python3

import pika
import logging

class AgeDifferenceFilter:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange='player_age', exchange_type='fanout')
        self.channel.queue_declare(queue='age', durable=True)
        self.channel.queue_bind(exchange='player_age', queue='age')

        self.channel.exchange_declare(exchange='database', exchange_type='direct')

        self.channel.queue_declare(queue='age_filter_terminator', durable=True)

        self.tag = self.channel.basic_consume(queue='age', auto_ack=True, on_message_callback=self.filter)
        self.channel.start_consuming()

    def filter(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == b'END':
            self.channel.basic_publish(exchange='', routing_key='age_filter_terminator', body='END',
                                       properties=pika.BasicProperties(delivery_mode=2,))
            return

        if body == b'CLOSE':
            self.channel.basic_cancel(self.tag)
            return

        data = body.decode().split(',')
        winner_age = int(data[4])
        loser_age = int(data[8])
        if winner_age - loser_age >= 20:
            winner_name = ' '.join([data[1], data[2]])
            loser_name = ' '.join([data[5], data[6]])
            result = '{}\t{}\t{}\t{}'.format(winner_age, winner_name, loser_age, loser_name)
            self.channel.basic_publish(exchange='database', routing_key='age', body=result,
                                       properties=pika.BasicProperties(delivery_mode=2,))
            logging.info('Sent %s' % result)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)

    filter = AgeDifferenceFilter()
