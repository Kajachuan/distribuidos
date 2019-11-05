#!/usr/bin/env python3

import pika
import logging
from datetime import datetime
from constants import HOST, END, OK, CLOSE, \
                      OUT_JOINER_EXCHANGE, \
                      OUT_AGE_CALCULATOR_EXCHANGE

END_ENCODED = END.encode()
CLOSE_ENCODED = CLOSE.encode()
AGE_CALCULATOR_QUEUE = 'joined_age'
TERMINATOR_QUEUE = 'calculator_terminator'

class AgeCalculator:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange=OUT_JOINER_EXCHANGE, exchange_type='fanout')
        self.channel.queue_declare(queue=AGE_CALCULATOR_QUEUE, durable=True)
        self.channel.queue_bind(exchange=OUT_JOINER_EXCHANGE, queue=AGE_CALCULATOR_QUEUE)

        self.channel.exchange_declare(exchange=OUT_AGE_CALCULATOR_EXCHANGE, exchange_type='fanout')

        self.channel.queue_declare(queue=TERMINATOR_QUEUE, durable=True)

    def run(self):
        self.tag = self.channel.basic_consume(queue=AGE_CALCULATOR_QUEUE, auto_ack=True,
                                              on_message_callback=self.calculate)
        self.channel.start_consuming()

    def calculate(self, ch, method, properties, body):
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
        tourney_date = data[0]
        winner_birthdate = data[4]
        loser_birthdate = data[8]
        if winner_birthdate == '' or loser_birthdate == '':
            return

        tourney_date = datetime.strptime(tourney_date, '%Y%m%d')
        winner_age = self._compute_age(datetime.strptime(winner_birthdate, '%Y%m%d'), tourney_date)
        loser_age = self._compute_age(datetime.strptime(loser_birthdate, '%Y%m%d'), tourney_date)
        data[4] = str(winner_age)
        data[8] = str(loser_age)
        body = ','.join(data)
        self.channel.basic_publish(exchange=OUT_AGE_CALCULATOR_EXCHANGE, routing_key='', body=body,
                                   properties=pika.BasicProperties(delivery_mode=2,))
        logging.info('Sent %s' % body)

    def _compute_age(self, birthdate, tourney_date):
        years = tourney_date.year - birthdate.year
        if tourney_date.month < birthdate.month or \
           (tourney_date.month == birthdate.month and tourney_date.day < birthdate.day):
            years -= 1
        return years

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)

    calculator = AgeCalculator()
    calculator.run()
