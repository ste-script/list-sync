#!/bin/bash
for container in $(docker ps -f name=broker -q)
do
    docker exec -u root $container tc qdisc add dev eth0 root netem rate 20mbit delay 300ms
done