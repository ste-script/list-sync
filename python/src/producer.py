from confluent_kafka import Producer, KafkaException
import time

conf = {
    'bootstrap.servers': 'localhost:9092',
    'security.protocol': 'PLAINTEXT',
}
producer = Producer(conf)

def delivery_report(err, msg):
    if err:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

try:
    while True:
        producer.produce("test-topic", value="test aloha", callback=delivery_report)
        time.sleep(0.001)
    producer.flush()
except KafkaException as e:
    print(f"Failed to connect to Kafka: {e}")
    exit(1)

exit()