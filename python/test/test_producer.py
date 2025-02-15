from pystream.consumer import Consumer
import unittest
from seed.seeder_pgsql import main
import json


class TestConsumer(unittest.TestCase):

    def __init__(self, methodName="runTest"):
        self.consumer = Consumer(
            group_id=10, callback=self.handler)
        super().__init__(methodName)

    def test_0_testProduceMessages(self):
        main()

    def test_1_testConsumeMessages(self):
        self.consumer.consume_messages()

    def handler(self, message):
        val = json.loads(message)
        if 'columns' in val:
            if len(val['columns']) > 1:
                if 'value' in val['columns'][1]:
                    if val['columns'][1]['value'] == 'stop':
                        self.consumer.stop()


if __name__ == '__main__':
    unittest.main()
