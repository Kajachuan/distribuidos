FROM python:3.7-alpine

RUN pip install pika

COPY ./accumulator/ /accumulator/
COPY ./constants/constants.py /accumulator/

WORKDIR /accumulator/
