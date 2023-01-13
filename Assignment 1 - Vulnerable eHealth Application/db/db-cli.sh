#!/usr/bin/bash
ID=$(docker ps | sed -n 2p | awk '{print $1;}')
docker exec -it $ID bash