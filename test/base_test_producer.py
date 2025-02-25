from list_sync.consumer import Consumer
from abc import ABC, abstractmethod
import json


class BaseTestProducer(ABC):
    def setUp(self):
        """Set up test environment"""
        self.consumer = Consumer(
            group_id=10,
            callback=self.handler
        )

    @abstractmethod
    def get_seeder(self):
        raise NotImplementedError

    def test_0_testProduceMessages(self):
        seeder = self.get_seeder()
        seeder()

    def test_1_testConsumeMessages(self):
        self.consumer.consume_messages()

    def handler(self, message):
        val = json.loads(message)
        if 'columns' in val:
            if len(val['columns']) > 1:
                if 'value' in val['columns'][1]:
                    if val['columns'][1]['value'] == 'stop':
                        self.consumer.stop()