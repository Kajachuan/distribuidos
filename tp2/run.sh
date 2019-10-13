#!/usr/bin/env bash

docker-compose up --build --scale surface_dispatcher=2 \
                          --scale joiner=2
