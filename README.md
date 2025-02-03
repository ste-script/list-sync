to run test first run on your local machine

sudo modprobe sch_netem

tc qdisc del dev eth0 root
tc qdisc add dev eth0 root netem rate 20mbit delay 300ms