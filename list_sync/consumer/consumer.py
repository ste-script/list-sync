from confluent_kafka import Consumer as KafkaConsumer, KafkaException, KafkaError
import uuid
import subprocess
import sys
import logging


class Consumer:
    def __init__(self, callback, group_id: str = uuid.uuid1(), topic_list: list = ['wal'], boostrap_servers: str = 'broker1:9092', simulate_latency: bool = False):
        self.logger = logging.getLogger(__name__)
        self.id = uuid.uuid1()
        self.conf = {
            # Ensure this matches the advertised listener
            'bootstrap.servers': boostrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        self.topic_list = topic_list
        self.running = True
        self.consumer = KafkaConsumer(self.conf)
        self.callback = callback
        if simulate_latency:
            self.set_network_latency()
        self.logger.info(f"Consumer {self.id} created")

    def consume_messages(self):
        try:
            self.consumer.subscribe(self.topic_list)
            while self.running:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        self.logger.info(f"End of partition reached {
                            msg.partition()}")
                    else:
                        raise KafkaException(msg.error())
                else:
                    msg_string = msg.value().decode('utf-8')
                    self.callback(msg_string)

        except KafkaException as e:
            self.logger.error(f"Failed to consume messages: {e}")
        finally:
            self.consumer.close()

    def stop(self):
        self.running = False

    def set_network_latency(self):
        try:
            latency = 200  # ms
            speed = 20  # mbit
            
            # First clear any existing rules
            cleanup_commands = [
                "tc qdisc del dev eth0 root 2>/dev/null || true",
                "tc qdisc del dev eth0 ingress 2>/dev/null || true"
            ]
            
            # Apply simpler traffic control that works in containers
            tc_commands = [
                # Outbound traffic control
                f"tc qdisc add dev eth0 root netem rate {speed}mbit delay {latency}ms",
                
                # Add basic ingress qdisc (works in most containers)
                "tc qdisc add dev eth0 handle ffff: ingress",
                # Apply policing to incoming traffic
                f"tc filter add dev eth0 parent ffff: protocol ip prio 1 u32 match ip src 0.0.0.0/0 police rate {speed}mbit burst 500k drop flowid :1"
            ]
            
            # Run all commands
            for cmd in cleanup_commands + tc_commands:
                try:
                    subprocess.run(cmd, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Command failed: {cmd} - {e}")
            
            self.logger.info(f"Traffic control set: {latency}ms latency, {speed}mbit limit (both directions)")
        except Exception as e:
            self.logger.error(f"Failed to set traffic control: {e}")

def fake_callback(msg):
    with open('/dev/null', 'w') as devnull:
        print(msg, file=devnull)

if __name__ == "__main__":
    from list_sync.consumer.writer.csv_writer import CsvWriter
    id = uuid.uuid1().__str__()
    simulate_latency = False
    writer = CsvWriter(consumer_id=id)
    callback = writer.write
    if len(sys.argv) > 1 and sys.argv[1] == 'simulate':
        simulate_latency = True
    if len(sys.argv) > 2:
        topic_list = sys.argv[2].split(',')
    else:
        topic_list = ['wal']

    if len(sys.argv) > 3:
        if sys.argv[3] == 'no-file':
            callback = fake_callback

    c = Consumer(callback=callback,
                 simulate_latency=simulate_latency, group_id=id, topic_list=topic_list)
    c.consume_messages()



