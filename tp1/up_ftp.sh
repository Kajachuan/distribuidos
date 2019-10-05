#!/usr/bin/env bash

for ((i = 1; i <= 2; i++)); do
  docker-compose run -d --name "pc$i" ftp_server
done
