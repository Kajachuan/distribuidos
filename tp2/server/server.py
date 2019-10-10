#!/usr/bin/env python3

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue='lines')

def callback(ch, method, properties, body):
    print("Received: %r" % body)

channel.basic_consume(queue='lines', auto_ack=True, on_message_callback=callback)

channel.start_consuming()
