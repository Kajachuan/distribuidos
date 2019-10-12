#!/usr/bin/env python3

import pika
import logging

class SurfaceDispatcher:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()
        self.channel.queue_declare(queue='lines')
        logging.info('Queue "lines" created')

        self.channel.exchange_declare(exchange='surfaces', exchange_type='direct')
        self.channel.basic_consume(queue='lines', auto_ack=True, on_message_callback=self.dispatch)

        self.channel.start_consuming()

    def dispatch(self, ch, method, properties, body):
        logging.info('Received: %r' % body)
        data = str(body).split(',')
        surface = data[3]
        minutes = '0' if data[9] == '' else data[9]
        self.channel.basic_publish(exchange='surfaces', routing_key=surface, body=minutes)
        logging.info('Sent %s to %s accumulator' % (minutes, surface))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    dispatcher = SurfaceDispatcher()
