#!/usr/bin/env python3

import pika
import logging
from constants import HOST, END, DATABASE_EXCHANGE, RESPONSE_EXCHANGE

FILES = ['surface', 'hand', 'age']

class Database:
    def __init__(self):
        self.count = 0
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange=DATABASE_EXCHANGE, exchange_type='direct')
        result = self.channel.queue_declare(queue='', durable=True, exclusive=True)
        self.queue_name = result.method.queue
        for filename in FILES:
            self.channel.queue_bind(exchange=DATABASE_EXCHANGE, queue=self.queue_name, routing_key=filename)

        self.channel.exchange_declare(exchange=RESPONSE_EXCHANGE, exchange_type='fanout')

    def run(self):
        self.tag = self.channel.basic_consume(queue=self.queue_name, auto_ack=True, on_message_callback=self.persist)
        self.channel.start_consuming()

    def persist(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        result = body.decode()
        if result == END:
            self.count += 1

            if self.count != 3:
                return

            for filename in FILES:
                file = open(filename, 'r')
                response = file.read()
                file.close()
                self.channel.basic_publish(exchange=RESPONSE_EXCHANGE, routing_key='', body=response,
                                           properties=pika.BasicProperties(delivery_mode=2,))
                self.channel.basic_cancel(self.tag)
            return

        file = open(method.routing_key, 'a+')
        file.write(result + '\n')
        file.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)
    database = Database()
    database.run()
