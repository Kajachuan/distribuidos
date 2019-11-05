FROM python:3.7-alpine

RUN pip install pika

COPY ./database/ /database/
COPY ./constants/constants.py /database/

WORKDIR /database/
