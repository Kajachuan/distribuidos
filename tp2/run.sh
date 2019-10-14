#!/usr/bin/env bash

docker-compose up --build \
                  --scale surface_dispatcher=2 \
                  --scale joiner=2 \
                  --scale age_calculator=2 \
                  --scale age_difference_filter=2 \
                  --scale different_hands_filter=2
