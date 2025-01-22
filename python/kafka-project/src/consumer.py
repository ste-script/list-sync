# filepath: /home/ste/Documents/list-sync/python/kafka-project/src/consumer.py
from confluent_kafka import Consumer, KafkaException, KafkaError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conf = {
    # Ensure this matches the advertised listener
    'bootstrap.servers': 'broker:9092',
    'group.id': 'my_consumer_group',
    'auto.offset.reset': 'earliest',
}

consumer = Consumer(conf)


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
                    logger.error(f"Error: {msg.error()}")
                    raise KafkaException(msg.error())
            else:
                logger.info(f"Received message: {msg.value().decode(
                    'utf-8')} from {msg.topic()} [{msg.partition()}]")

    except KafkaException as e:
        logger.error(f"Failed to consume messages: {e}")
    finally:
        consumer.close()


if __name__ == "__main__":
    consume_messages()
