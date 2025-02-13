import sys
import json
from datetime import datetime

import mysql.connector
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent
from pystream.connector.producer import Producer


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class MysqlConnector:

    def __init__(self, conf: dict = {
        'host': 'db',
        'port': 3306,
        'user': 'repl_user',
        'passwd': 'repl_password',
        'database': 'exampledb',
        'table': 'example_table'
    }):
        kafka_conf = conf.get('kafka_conf', False)
        if kafka_conf:
            self.producer = Producer(conf=kafka_conf)
        else:
            self.producer = Producer()
        self.conf = conf
        self.pk_columns = []

    def fetch_primary_key_columns(self, host, port, user, password, db, table):
        """Retrieve primary key columns for the specified table."""
        query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = %s 
            AND COLUMN_KEY = 'PRI'
        """
        with mysql.connector.connect(
                host=host, port=port, user=user, password=password, database=db
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (db, table))
                self.pk_columns = [row[0] for row in cursor.fetchall()]

    def process_event(self, event, row):
        """
        Process an individual binlog event row and generate a payload
        in a format similar to PostgreSQL's wal2json.
        """
        # Work on a copy to avoid modifying the original row.
        row_data = row.copy()

        # Determine event type specifics.
        if isinstance(event, WriteRowsEvent):
            action = 'I'
            data = row_data.get('values', {})
            before_values = None
        elif isinstance(event, UpdateRowsEvent):
            action = 'U'
            before_values = row_data.get('before_values', {})
            data = row_data.get('after_values', {})
        elif isinstance(event, DeleteRowsEvent):
            action = 'D'
            before_values = row_data.get('values', {})
            data = None
        else:
            raise ValueError(f"Unsupported event type: {type(event)}")

        # For update and delete events, use the before-values to extract primary keys;
        # for inserts, use the values.
        pk_source = data if action == 'I' else before_values
        pk_data = {col: pk_source.get(col) for col in self.pk_columns}

        # Build the payload sections.
        identity = [{'name': k, 'value': v}
                    for k, v in (before_values or {}).items()]
        columns = [{'name': k, 'value': v} for k, v in (data or {}).items()]
        payload = {
            'action': action,
            'table': event.table,
            'schema': event.schema,
            'columns': columns,
            'identity': identity,
            'pk': [{'name': col, 'value': pk_data.get(col)} for col in self.pk_columns],
        }
        payload_json = json.dumps(payload, cls=DateTimeEncoder)

        # Determine a key from the first primary key column.
        key_value = pk_data.get(self.pk_columns[0])
        if key_value is None:
            raise ValueError(
                f"Primary key column {self.pk_columns[0]} not found in payload"
            )

        return payload_json, str(key_value).encode()

    def connect(self):
        # Get primary key columns for the target table
        pk_columns = self.fetch_primary_key_columns(
            self.conf['host'],
            self.conf['port'],
            self.conf['user'],
            self.conf['passwd'],
            self.conf['database'],
            self.conf['table']
        )

        if not pk_columns:
            raise ValueError(
                f"Primary key not found for {self.conf['database']}.{self.conf['table']}")

    # Initialize MySQL binlog stream
        MYSQL_CONFIG = {
            'host': self.conf['host'],
            'port': self.conf['port'],
            'user': self.conf['user'],
            'passwd': self.conf['passwd'],
        }

        stream = BinLogStreamReader(
            connection_settings=MYSQL_CONFIG,
            server_id=101,  # Unique ID for replication client
            resume_stream=True,
            only_events=[WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent],
            only_tables=[self.conf['table']],
            only_schemas=[self.conf['database']],
            blocking=True,
        )
        print("Starting MySQL replication stream...", file=sys.stderr)
        try:
            for event in stream:
                for row in event.rows:
                    try:
                        payload, key = self.process_event(event, row)
                        self.producer.send_message(payload, key)
                    except Exception as e:
                        print(f"Error processing event: {e}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\nReplication stream stopped.", file=sys.stderr)
        finally:
            self.producer.close()
            stream.close()


if __name__ == '__main__':
    m = MysqlConnector()
    m.connect()
