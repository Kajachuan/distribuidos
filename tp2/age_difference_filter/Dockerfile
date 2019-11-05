FROM python:3.7-alpine

RUN pip install pika

COPY ./age_difference_filter/ /age_difference_filter/
COPY ./constants/constants.py /age_difference_filter/

WORKDIR /age_difference_filter/
