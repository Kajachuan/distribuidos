FROM python:3.7-alpine

RUN pip install pika

COPY ./percentage_calculator/ /percentage_calculator/
COPY ./constants/constants.py /percentage_calculator/

WORKDIR /percentage_calculator/
