from pystream.consumer import Consumer
from pystream.consumer.writer import CsvWriter
import unittest
import io

class TestConsumer(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
    
    def test_consume_messages(self):
        consumer = Consumer(group_id=6, writer= CsvWriter(filename='data/output'))
        consumer.consume_messages()


if __name__ == '__main__':
    unittest.main()