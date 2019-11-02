#!/usr/bin/env python3

import pika
import logging

FILES = ['surface', 'hand', 'age']

class Database:
    def __init__(self):
        self.count = 0
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange='database', exchange_type='direct')
        self.channel.queue_declare(queue='results', durable=True)

        for filename in FILES:
            self.channel.queue_bind(exchange='database', queue='results', routing_key=filename)

        self.channel.queue_declare(queue='response', durable=True)

        self.tag = self.channel.basic_consume(queue='results', auto_ack=True, on_message_callback=self.persist)
        self.channel.start_consuming()

    def persist(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        result = body.decode()
        if result == 'END':
            self.count += 1

            if self.count != 3:
                return

            for filename in FILES:
                file = open(filename, 'r')
                response = file.read()
                file.close()
                self.channel.basic_publish(exchange='', routing_key='response', body=response,
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
