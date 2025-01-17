from confluent_kafka import Consumer, KafkaException, KafkaError

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest',
    'security.protocol': 'PLAINTEXT',
}
consumer = Consumer(conf)

def consume_messages():
    try:
        consumer.subscribe(['test-topic'])

        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached {msg.partition()}")
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                print(f"Received message: {msg.value().decode('utf-8')} from {msg.topic()} [{msg.partition()}]")

    except KafkaException as e:
        print(f"Failed to consume messages: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_messages()