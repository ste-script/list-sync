from confluent_kafka import Producer, KafkaException

conf = {
    'bootstrap.servers': 'broker1:9092',
    'security.protocol': 'PLAINTEXT',
    "queue.buffering.max.messages": 10000000,
    'compression.type': 'lz4',
    'linger.ms': 300,
    'batch.num.messages': 1000000,
    'batch.size': 100000000,
}
producer = Producer(conf)


def delivery_report(err, msg):
    if err:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def send_message(msg):
    try:
        producer.produce("wal", value=msg, on_delivery=delivery_report)
        producer.poll(0)
    except KafkaException as e:
        print(f"Failed to produce message: {e}")
