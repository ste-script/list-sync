from confluent_kafka import Producer, KafkaException

conf = {
    'bootstrap.servers': 'broker:9092',
    'security.protocol': 'PLAINTEXT',
}
producer = Producer(conf)


def delivery_report(err, msg):
    if err:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def send_message(msg):
    try:
        producer.produce("wal", value=msg, callback=delivery_report)
    except KafkaException as e:
        print(f"Failed to produce message: {e}")
