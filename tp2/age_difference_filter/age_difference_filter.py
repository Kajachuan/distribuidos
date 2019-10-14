#!/usr/bin/env python3

import pika
import logging

class AgeDifferenceFilter:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.queue_declare(queue='age', durable=True)

        self.channel.queue_declare(queue='database', durable=True)

        self.tag = self.channel.basic_consume(queue='age', auto_ack=True, on_message_callback=self.filter)
        self.channel.start_consuming()

    def filter(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        if body == b'END':
            self.channel.basic_publish(exchange='', routing_key='database', body='END,age',
                                       properties=pika.BasicProperties(delivery_mode=2,))
            self.channel.basic_cancel(self.tag)
            return

        data = body.decode().split(',')
        winner_age = int(data[4])
        loser_age = int(data[8])
        if winner_age - loser_age >= 20:
            winner_name = ' '.join([data[1], data[2]])
            loser_name = ' '.join([data[5], data[6]])
            result = '{}\t{}\t{}\t{}'.format(winner_age, winner_name, loser_age, loser_name)
            self.channel.basic_publish(exchange='', routing_key='database', body=','.join([result, 'age']),
                                       properties=pika.BasicProperties(delivery_mode=2,))
            logging.info('Sent %s' % result)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)

    filter = AgeDifferenceFilter()
