from pystream.consumer import Consumer
from pystream.connector.producer import Producer
import unittest


class TestConsumer(unittest.TestCase):

    def __init__(self, methodName="runTest"):
        self.handler = Consumer(
            group_id=10, callback=self.handler)
        super().__init__(methodName)
        self.producer = Producer()

    def test_0_testProduceMessages(self):
        for i in range(1_000_000):
            self.producer.send_message(f'testMessage{i}')
        self.producer.send_message('stop')

    def test_1_testConsumeMessages(self):
        self.handler.consume_messages()

    def handler(self, message):
        if message == 'stop':
            self.handler.stop()


if __name__ == '__main__':
    unittest.main()
