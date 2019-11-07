#!/usr/bin/env python3

import logging
import pika
from constants import HOST, END, CLOSE, OK, \
                      OUT_AGE_CALCULATOR_EXCHANGE, DATABASE_EXCHANGE

END_ENCODED = END.encode()
CLOSE_ENCODED = CLOSE.encode()
AGE_DIFFERENCE_FILTER_QUEUE = 'age'
TERMINATOR_EXCHANGE = 'age_filter_terminator'

class AgeDifferenceFilter:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange=OUT_AGE_CALCULATOR_EXCHANGE, exchange_type='fanout')
        self.channel.queue_declare(queue=AGE_DIFFERENCE_FILTER_QUEUE, durable=True)
        self.channel.queue_bind(exchange=OUT_AGE_CALCULATOR_EXCHANGE, queue=AGE_DIFFERENCE_FILTER_QUEUE)

        self.channel.exchange_declare(exchange=DATABASE_EXCHANGE, exchange_type='direct')
        self.channel.exchange_declare(exchange=TERMINATOR_EXCHANGE, exchange_type='fanout')

    def run(self):
        self.tag = self.channel.basic_consume(queue=AGE_DIFFERENCE_FILTER_QUEUE, auto_ack=True,
                                              on_message_callback=self.filter)
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
        winner_age = int(data[4])
        loser_age = int(data[8])
        if winner_age - loser_age >= 20:
            winner_name = ' '.join([data[1], data[2]])
            loser_name = ' '.join([data[5], data[6]])
            result = '{}\t{}\t{}\t{}'.format(winner_age, winner_name, loser_age, loser_name)
            self.channel.basic_publish(exchange=DATABASE_EXCHANGE, routing_key=AGE_DIFFERENCE_FILTER_QUEUE, body=result,
                                       properties=pika.BasicProperties(delivery_mode=2,))
            logging.info('Sent %s' % result)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)

    filter = AgeDifferenceFilter()
    filter.run()
