#!/bin/bash

# Add latency to all containers with the name "broker"
# This is useful for testing the broker's ability to handle latency
for container in $(docker ps -f name=broker -q)
do
    # First clear any existing rules
    docker exec -u root $container bash -c "tc qdisc del dev eth0 root 2>/dev/null || true"
    docker exec -u root $container bash -c "tc qdisc del dev eth0 ingress 2>/dev/null || true"
    
    # Set parameters
    LATENCY="10ms"
    RATE="1000mbit"
    BURST="1000k"
    
    # Apply outbound traffic control
    docker exec -u root $container tc qdisc add dev eth0 root netem rate $RATE delay $LATENCY
    
    # Add ingress qdisc for inbound traffic control
    docker exec -u root $container tc qdisc add dev eth0 handle ffff: ingress
    
    # Apply policing to incoming traffic
    docker exec -u root $container tc filter add dev eth0 parent ffff: protocol ip prio 1 u32 match ip src 0.0.0.0/0 police rate $RATE burst $BURST drop flowid :1
    
    echo "Added bidirectional traffic control to container $container: $RATE bandwidth, $LATENCY latency"
done