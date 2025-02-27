from list_sync.consumer import Consumer
import unittest
import json


class TestConsumer(unittest.TestCase):

    def setUp(self, methodName="runTest"):
        super().setUp()
        self.consumer = Consumer(callback=self.handler, simulate_latency=True, topic_list=['wal_pg'])

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
