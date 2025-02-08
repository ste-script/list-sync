from pystream.consumer import Consumer
from pystream.connector.producer import send_message
import unittest


class TestConsumer(unittest.TestCase):

    def __init__(self, methodName="runTest"):
        self.handler = Consumer(
            group_id=10, callback=self.handler)
        super().__init__(methodName)

    def test_0_testProduceMessages(self):
        for i in range(1_000_000):
            send_message(f'testMessage{i}')
        send_message('stop')

    def test_1_testConsumeMessages(self):
        self.handler.consume_messages()

    def handler(self, message):
        if message == 'stop':
            self.handler.stop()


if __name__ == '__main__':
    unittest.main()
