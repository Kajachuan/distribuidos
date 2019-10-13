#!/usr/bin/env python3

import pika
import logging
from datetime import datetime

class AgeCalculator:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange='joined', exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange='joined', queue=queue_name)

        self.channel.exchange_declare(exchange='age', exchange_type='direct')

        self.channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=self.calculate)
        self.channel.start_consuming()

    def calculate(self, ch, method, properties, body):
        logging.info('Received %r' % body)
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
        self.channel.basic_publish(exchange='age', routing_key='', body=body)
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
                        level=logging.INFO)

    calculator = AgeCalculator()
