from abc import ABC, abstractmethod
import unittest
import json


class BaseTestProducer(ABC, unittest.TestCase):
    def setUp(self):
        """Set up test environment - should be overridden by subclasses"""
        pass

    @abstractmethod
    def get_seeder(self):
        """Return the appropriate seeder module for the database type"""
        pass

    def test_0_produce_messages(self):
        """Test producing messages using the seeder"""
        seeder = self.get_seeder()
        seeder()

    def test_1_consume_messages(self):
        """Test consuming messages"""
        self.consumer.consume_messages()

    def handler(self, message):
        """Handle incoming messages"""
        val = json.loads(message)
        if 'columns' in val:
            if len(val['columns']) > 1:
                if 'value' in val['columns'][1]:
                    if val['columns'][1]['value'] == 'stop':
                        self.consumer.stop()