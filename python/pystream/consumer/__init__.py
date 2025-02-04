from confluent_kafka import Consumer as KafkaConsumer, KafkaException, KafkaError
import uuid
import subprocess
import sys
import logging


class Consumer:
    def __init__(self, writer, group_id: str = uuid.uuid1(), topic: str = 'wal', boostrap_servers: str = 'broker1:9092', simulate_latency: bool = False):
        self.logger = logging.getLogger(__name__)
        self.id = uuid.uuid1()
        self.conf = {
            # Ensure this matches the advertised listener
            'bootstrap.servers': boostrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        self.topic = topic
        self.consumer = KafkaConsumer(self.conf)
        self.writer = writer
        if simulate_latency:
            self.set_network_latency()
        self.logger.info(f"Consumer {self.id} created")


    def consume_messages(self):
        try:
            self.consumer.subscribe(['wal'])
            while True:
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
                    self.writer.write_to_file(msg_string)

        except KafkaException as e:
            self.logger.error(f"Failed to consume messages: {e}")
        finally:
            self.consumer.close()


    def set_network_latency(self):
        try:
            latency = 800  # ms
            speed = 20  # mbit
            subprocess.run(
                f"tc qdisc add dev eth0 root netem rate {
                    speed}mbit delay {latency}ms",
                shell=True,
                check=True
            )
            self.logger.info(f"Network latency set to {
                latency}ms and speed to {speed}mbit")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to set network latency: {e}")


if __name__ == "__main__":
    from pystream.consumer.writer.csv_writer import CsvWriter
    id = uuid.uuid1().__str__()
    simulate_latency = False
    if len(sys.argv) > 1 and sys.argv[1] == 'simulate':
        simulate_latency = True
    c = Consumer(writer=CsvWriter(consumer_id=id),
                 simulate_latency=simulate_latency, group_id=id)
    c.consume_messages()
