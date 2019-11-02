#!/usr/bin/env python3

import os
import pika
import logging

class Terminator:
    def __init__(self, processes_number, in_queue, group_queue, next_exchange, next_exchange_type, next_routing_keys):
        self.processes_number = processes_number
        self.in_queue = in_queue
        self.group_queue = group_queue
        self.next_exchange = next_exchange
        self.next_routing_keys = next_routing_keys

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = connection.channel()

        self.channel.queue_declare(queue=in_queue, durable=True)
        self.channel.queue_declare(queue=group_queue, durable=True)

        self.channel.exchange_declare(exchange=next_exchange, exchange_type=next_exchange_type)

    def run(self):
        self.tag = self.channel.basic_consume(queue=self.in_queue, auto_ack=True, on_message_callback=self.close)
        self.channel.start_consuming()

    def close(self, ch, method, properties, body):
        if body != b'END':
            return

        for i in range(self.processes_number):
            self.channel.basic_publish(exchange='', routing_key=self.group_queue, body='CLOSE',
                                       properties=pika.BasicProperties(delivery_mode=2,))

        for routing_key in self.next_routing_keys.split('-'):
            self.channel.basic_publish(exchange=self.next_exchange, routing_key=routing_key, body='END',
                                       properties=pika.BasicProperties(delivery_mode=2,))

        self.channel.basic_cancel(self.tag)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.ERROR)

    processes_number = int(os.environ['PROCESSES_NUMBER'])
    in_queue = os.environ['IN_QUEUE']
    group_queue = os.environ['GROUP_QUEUE']
    next_exchange = os.environ['NEXT_EXCHANGE']
    next_exchange_type = os.environ['NEXT_EXCHANGE_TYPE']
    next_routing_keys = os.environ['NEXT_ROUTING_KEYS']

    terminator = Terminator(processes_number, in_queue,
                            group_queue, next_exchange,
                            next_exchange_type, next_routing_keys)
    terminator.run()
