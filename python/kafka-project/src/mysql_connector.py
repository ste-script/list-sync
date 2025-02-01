import sys
import json
import time
from datetime import datetime

import mysql.connector
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent
from producer import send_message

# MySQL connection configuration
MYSQL_CONFIG = {
    'host': 'db',
    'port': 3306,
    'user': 'repl_user',
    'passwd': 'repl_password'
}

# Database and table configuration
DATABASE = 'exampledb'
TABLE = 'example_table'


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def fetch_primary_key_columns(host, port, user, password, db, table):
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
            pk_columns = [row[0] for row in cursor.fetchall()]
    return pk_columns


# Get primary key columns for the target table
pk_columns = fetch_primary_key_columns(
    MYSQL_CONFIG['host'],
    MYSQL_CONFIG['port'],
    MYSQL_CONFIG['user'],
    MYSQL_CONFIG['passwd'],
    DATABASE,
    TABLE
)

if not pk_columns:
    raise ValueError(f"Primary key not found for {DATABASE}.{TABLE}")

# Initialize MySQL binlog stream
stream = BinLogStreamReader(
    connection_settings=MYSQL_CONFIG,
    server_id=101,  # Unique ID for replication client
    resume_stream=True,
    only_events=[WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent],
    only_tables=[TABLE],
    only_schemas=[DATABASE],
    blocking=True,
)


def process_event(event, row):
    """
    Process an individual binlog event row and generate a payload
    in a format similar to PostgreSQL's wal2json.
    """
    # Copy row data to avoid in-place modifications
    row_data = row.copy()

    if isinstance(event, WriteRowsEvent):
        action = 'I'
        data = row_data.get('values', {})
        pk_data = {col: data.get(col) for col in pk_columns}
        before_values = None
    elif isinstance(event, UpdateRowsEvent):
        action = 'U'
        # For updates, we take the "after" values as the new state
        data = row_data.get('after_values', {})
        pk_data = {col: row_data.get('before_values', {}).get(col) for col in pk_columns}
        before_values = row_data.get('before_values', {})
    elif isinstance(event, DeleteRowsEvent):
        action = 'D'
        # For deletes, only "before" values exist
        data = None
        before_values = row_data.get('values', {})
        pk_data = {col: before_values.get(col) for col in pk_columns}
    else:
        raise ValueError(f"Unsupported event type: {type(event)}")

    # Build identity and column payload sections
    identity = [{'name': k, 'value': v} for k, v in (before_values or {}).items()]
    columns = [{'name': k, 'value': v} for k, v in (data or {}).items()]

    payload = {
        'action': action,
        'table': event.table,
        'schema': event.schema,
        'columns': columns,
        'identity': identity,
        'pk': [{'name': col, 'value': pk_data.get(col)} for col in pk_columns]
    }

    payload_json = json.dumps(payload, cls=DateTimeEncoder)

    # Determine a key from the first primary key column
    try:
        # Use the first primary key in pk_data (assumes 'id' or similar)
        key_value = pk_data[pk_columns[0]]
    except KeyError:
        raise ValueError(f"Primary key column {pk_columns[0]} not found in payload")

    return payload_json, str(key_value).encode()


def main():
    print("Starting MySQL replication stream...", file=sys.stderr)
    try:
        for event in stream:
            for row in event.rows:
                try:
                    payload, key = process_event(event, row)
                    send_message(payload, key)
                except Exception as e:
                    print(f"Error processing event: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nReplication stream stopped.", file=sys.stderr)
    finally:
        stream.close()


if __name__ == '__main__':
    main()
