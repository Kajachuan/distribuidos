FROM python:3.7-alpine

RUN pip install pika

COPY client.py /client/
COPY /data /client/data

WORKDIR /client/
