to run test first run on your local machine

sudo modprobe sch_netem

tc qdisc del dev eth0 root
tc qdisc add dev eth0 root netem rate 20mbit delay 300ms

test with protobuf each consumer consumed 98mb
test completed into 136 sec abd seeding completed into  60 sec

also with test with plain json consumer consumed 98mb so stay with it