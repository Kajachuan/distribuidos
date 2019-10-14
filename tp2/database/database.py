#!/usr/bin/env python3

import pika
import logging

FILES = ['surface', 'hand', 'age']

class Database:
    def __init__(self):
        self.count = 0
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.queue_declare(queue='database', durable=True)
        self.channel.queue_declare(queue='response', durable=True)

        self.tag = self.channel.basic_consume(queue='database', auto_ack=True, on_message_callback=self.persist)
        self.channel.start_consuming()

    def persist(self, ch, method, properties, body):
        logging.info('Received %r' % body)
        [response, filename] = body.decode().split(',')
        if response == 'END':
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

        file = open(filename, 'a+')
        file.write(response + '\n')
        file.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    database = Database()
