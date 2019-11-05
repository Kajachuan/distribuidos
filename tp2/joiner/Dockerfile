FROM python:3.7-alpine

RUN pip install pika

COPY ./joiner/ /joiner/
COPY ./constants/constants.py /joiner/

WORKDIR /joiner/
