from consumer import Consumer
from consumer.writer import CsvWriter
import unittest
import io

class TestConsumer(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
    
    def test_consume_messages(self):
        consumer = Consumer(CsvWriter())
        consumer.consume_messages()


if __name__ == '__main__':
    unittest.main()