FROM python:3.7-alpine

RUN pip install pika

COPY ./terminator/ /terminator/
COPY ./constants/constants.py /terminator/

WORKDIR /terminator/
