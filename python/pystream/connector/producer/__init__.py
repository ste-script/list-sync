from confluent_kafka import Producer as Kproducer, KafkaException
from pystream.proto.message_pb2 import WalMessage
import time

_base_conf = {
    'bootstrap.servers': 'broker1:9092',
    'security.protocol': 'PLAINTEXT',
    "queue.buffering.max.messages": 10000000,
    'compression.type': 'lz4',
    'linger.ms': 1000,
    'batch.num.messages': 1000000,
    'batch.size': 100000000,
    'topic': 'wal'
}


class Producer:
    def __init__(self, conf: dict = _base_conf):
        self.topic = conf.pop('topic')
        self.producer = Kproducer(conf)

    def delivery_report(self, err, msg):
        if err:
            print(f"Message delivery failed: {err}")

    def send_message(self, payload, key=None):
        try:
            # Create protobuf message
            message = WalMessage()
            message.payload = payload if isinstance(payload, bytes) else payload.encode()
            message.timestamp = int(time.time() * 1000)
            if key:
                message.key = key

            # Serialize and send
            serialized_message = message.SerializeToString()
            self.producer.produce(
                topic=self.topic,
                value=serialized_message,
                key=key,
                on_delivery=self.delivery_report
            )
            self.producer.poll(0)
        except KafkaException as e:
            print(f"Failed to produce message: {e}")

    def close(self):
        self.producer.flush()