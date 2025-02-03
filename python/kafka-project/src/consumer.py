# filepath: /home/ste/Documents/list-sync/python/kafka-project/src/consumer.py
from confluent_kafka import Consumer, KafkaException, KafkaError
import logging
import uuid
import subprocess
from csv_writer import CsvWriter
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
id = uuid.uuid1()
conf = {
    # Ensure this matches the advertised listener
    'bootstrap.servers': 'broker1:9092',
    'group.id': id,
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
writer = CsvWriter(
    filename='./test/data/output',
    consumer_id=id.__str__(),
    split_updates=False,
    split_files=False
)

def consume_messages():
    try:
        consumer.subscribe(['wal'])
        logger.info("Subscribed to topic 'wal'")

        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info(f"End of partition reached {msg.partition()}")
                else:
                    raise KafkaException(msg.error())
            else:
                msg_string = msg.value().decode('utf-8')
                writer.write_to_file(msg_string, consumer_id=id.__str__())

    except KafkaException as e:
        logger.error(f"Failed to consume messages: {e}")
    finally:
        consumer.close()


def set_network_latency():
    try:
        latency = 800  # ms
        speed = 20  # mbit
        subprocess.run(
            f"tc qdisc add dev eth0 root netem rate {
                speed}mbit delay {latency}ms",
            shell=True,
            check=True
        )
        logger.info(f"Network latency set to {
                    latency}ms and speed to {speed}mbit")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set network latency: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'simulate':
        set_network_latency()
    consume_messages()
