import sys
import json
from producer import send_message
from datetime import datetime
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
)
import mysql.connector

# MySQL connection configuration
mysql_config = {
    'host': 'mysql',
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
        return super(DateTimeEncoder, self).default(obj)


def fetch_primary_key_columns(host, port, user, password, db, table):
    """Retrieve primary key columns for the specified table."""
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = %s 
        AND COLUMN_KEY = 'PRI'
    """, (db, table))
    pk_columns = [col[0] for col in cursor.fetchall()]
    cursor.close()
    conn.close()
    return pk_columns


# Get primary key columns for the target table
pk_columns = fetch_primary_key_columns(
    mysql_config['host'],
    mysql_config['port'],
    mysql_config['user'],
    mysql_config['passwd'],
    DATABASE,
    TABLE
)

if not pk_columns:
    raise ValueError(f"Primary key not found for {DATABASE}.{TABLE}")

# Initialize MySQL binlog stream
stream = BinLogStreamReader(
    connection_settings=mysql_config,
    server_id=100,  # Unique ID for replication client
    blocking=True,
    resume_stream=True,
    only_events=[WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent],
    only_tables=[TABLE],
    only_schemas=[DATABASE]
)


def process_event(event, row):
    """Process individual binlog event row and generate Kafka message."""
    # Determine event type and extract values
    print(f"Processing event: {row}", file=sys.stderr)
    if isinstance(event, WriteRowsEvent):
        action = 'I'
        values = row['values']
        pk_data = {col: values[col] for col in pk_columns}
    elif isinstance(event, UpdateRowsEvent):
        action = 'U'
        row['values'] = row['after_values']
        pk_data = {col: row['before_values'][col] for col in pk_columns}
    elif isinstance(event, DeleteRowsEvent):
        action = 'D'
        row['before_values'] = row['values']
        del row['values']
        pk_data = {col: row['before_values'] for col in pk_columns}
    else:
        raise ValueError(f"Unsupported event type: {event}")

    # Construct payload matching PostgreSQL wal2json format
    if 'before_values' in row:
        identity = [{'name': k, 'value': v}
                    for k, v in row['before_values'].items()]
    else:
        identity = []

    if 'values' in row:
        columns = [{'name': k, 'value': v} for k, v in row['values'].items()]
    else:
        columns = []

    payload = {
        'action': action,
        'table': event.table,
        'schema': event.schema,
        'columns': columns,
        'identity': identity,
        'pk': [{'name': col, 'value': pk_data[col]} for col in pk_columns]
    }
    print(f"Generated payload: {payload}", file=sys.stderr)

    # Serialize payload and extract primary key
    payload_json = json.dumps(payload, cls=DateTimeEncoder)
    try:
        key = str(next(item['value']
                  for item in payload['pk'] if item['name'] == 'id'))
    except StopIteration:
        raise ValueError("Primary key 'id' not found in payload")

    return payload_json, key.encode()


print("Starting MySQL replication stream...", file=sys.stderr)
try:
    for event in stream:
        for row in event.rows:
            try:
                payload, key = process_event(event, row)
                if payload and key:
                    send_message(payload, key)
            except Exception as e:
                print(f"Error processing event: {e}", file=sys.stderr)
except KeyboardInterrupt:
    stream.close()
    print("\nReplication stream stopped.", file=sys.stderr)
