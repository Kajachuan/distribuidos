#!/usr/bin/env bash

# sudo docker-compose build
sudo docker-compose up --scale client_analyze=3 --scale client_report=2
