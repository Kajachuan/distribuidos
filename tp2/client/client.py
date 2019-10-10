#!/usr/bin/env python3

import pika
from glob import glob

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue='lines')

for filename in glob('./data/atp_matches_*.csv'):
    with open(filename, 'r') as file:
        for line in iter(file.readline, ''):
            channel.basic_publish(exchange='', routing_key='lines', body=line)
            print("Sent: " + line)

connection.close()
