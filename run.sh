#!/usr/bin/env bash

sudo docker-compose build
sudo docker-compose up --scale client=5
