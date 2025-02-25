from base_test_producer import BaseTestProducer
from list_sync.consumer import Consumer
import unittest


class PostgreSQLTestProducer(BaseTestProducer, unittest.TestCase):
    def setUp(self):
        """Set up PostgreSQL-specific test environment"""
        super().setUp()
        self.consumer = Consumer(
            group_id=10,
            callback=self.handler,
            topic_list=['wal_pg']
        )

    def get_seeder(self):
        """Return the PostgreSQL seeder module"""
        from seed.seeder_pgsql import main
        return main


if __name__ == '__main__':
    unittest.main()
