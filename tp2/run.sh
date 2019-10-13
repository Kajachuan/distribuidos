#!/usr/bin/env bash

docker-compose up --build --scale different_hands_filter=2 \
                          --scale age_calculator=2
