#!/bin/bash

# Add latency to all containers with the name "broker"
# This is useful for testing the broker's ability to handle latency
# The latency is set to 300ms so the ping time between the brokers is 600ms
for container in $(docker ps -f name=broker -q)
do
    docker exec -u root $container tc qdisc add dev eth0 root netem rate 20mbit delay 150ms
done