from base_test_producer import BaseTestProducer
from pystream.consumer import Consumer
import unittest


class MysqlTestProducer(BaseTestProducer, unittest.TestCase):
    def setUp(self):
        """Set up Mysql-specific test environment"""
        super().setUp()
        self.consumer = Consumer(
            group_id=12,
            callback=self.handler,
            topic_list=['wal_my']
        )

    def get_seeder(self):
        """Return the Mysql seeder module"""
        from seed.seeder_mysql import main
        return main


if __name__ == '__main__':
    unittest.main()
