from pystream.connector.mysql_connector import MysqlConnector
from . import pgsql_connector

__all__ = ['mysql_connector', 'pgsql_connector']


class Connector:
    def __init__(self,
                 db_type: str = 'mysql',
                 host: str = 'db',
                 port: int = 3306,
                 user: str = 'repl_user',
                 password: str = 'repl_password',
                 database: str = 'exampledb',
                 table: str = 'example_table',
                 topic: str = 'wal_mysql',
                 kafka_conf: dict = ()
                 ):
        conf = {
            'host': host,
            'port': port,
            'user': user,
            'passwd': password,
            'database': database,
            'table': table,
            'topic': topic,
            'kafka_conf': kafka_conf
        }
        if db_type == 'mysql':
            self.connector = MysqlConnector(conf=conf)
        elif db_type == 'pgsql':
            self.connector = PgsqlConnector(conf=conf)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def connect(self):
        return self.connector.connect()
