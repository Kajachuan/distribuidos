#!/usr/bin/env bash

docker-compose up --build \
                  --scale surface_dispatcher=1 \
                  --scale joiner=1 \
                  --scale age_calculator=1 \
                  --scale age_difference_filter=1 \
                  --scale different_hands_filter=1
