#!/usr/bin/env python3

import pika
import logging
from glob import glob

class Client:
    def __init__(self):
        self.results = 0
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='response', durable=True)

        self.channel.exchange_declare(exchange='players', exchange_type='fanout')
        self.channel.exchange_declare(exchange='matches', exchange_type='fanout')

    def run(self):
        self.send_players_data()
        self.send_matches_data()

        self.tag = self.channel.basic_consume(queue='response', auto_ack=True, on_message_callback=self.print_response)
        self.channel.start_consuming()

    def send_players_data(self):
        with open('./data/atp_players.csv', 'r') as file:
            file.readline()
            for line in iter(file.readline, ''):
                self.channel.basic_publish(exchange='players', routing_key='', body=line,
                                           properties=pika.BasicProperties(delivery_mode=2,))
                logging.info('Sent %s' % line)

        self.channel.basic_publish(exchange='players', routing_key='', body='END',
                                   properties=pika.BasicProperties(delivery_mode=2,))

    def send_matches_data(self):
        for filename in glob('./data/atp_matches_*.csv'):
            with open(filename, 'r') as file:
                file.readline()
                for line in iter(file.readline, ''):
                    self.channel.basic_publish(exchange='matches', routing_key='', body=line,
                                               properties=pika.BasicProperties(delivery_mode=2,))
                    logging.info('Sent %s' % line)

        self.channel.basic_publish(exchange='matches', routing_key='', body='END',
                                   properties=pika.BasicProperties(delivery_mode=2,))

    def print_response(self, ch, method, properties, body):
        print(body.decode())
        self.results += 1
        if self.results == 3:
            self.channel.basic_cancel(self.tag)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)
    client = Client()
    client.run()
