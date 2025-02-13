from confluent_kafka import Producer as Kproducer, KafkaException

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

    def send_message(self, msg, key=None):
        try:
            self.producer.produce(topic=self.topic, value=msg, key=key,
                                  on_delivery=self.delivery_report)
            self.producer.poll(0)
        except KafkaException as e:
            print(f"Failed to produce message: {e}")

    def close(self):
        self.producer.flush()
