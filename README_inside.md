# list_sync

A Python library for synchronizing database changes through Apache Kafka using Change Data Capture (CDC).

## Features

- Database change capture support:
  - MySQL with row-based replication
  - PostgreSQL with logical replication (wal2json)
- Kafka message streaming with configurable topics
- CSV output support
- Network latency simulation
- Batch processing capabilities

## Installation

```bash
poetry install
```

## Quick Start

### PostgreSQL Connector

```python
from list_sync.connector import PgsqlConnector

connector = PgsqlConnector(
    conf={
        'host': 'localhost',
        'port': '5432',
        'user': 'postgres',
        'passwd': 'postgres',
        'database': 'mydb',
        'table': 'mytable'
    },
    topic=['wal_pg']
)

connector.connect()
```

### MySQL Connector

```python
from list_sync.connector import MysqlConnector

connector = MysqlConnector(
    conf={
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'passwd': 'password',
        'database': 'mydb',
        'table': 'mytable'
    },
    topic=['wal_my']
)

connector.connect()
```

### Consumer Usage

```python
from list_sync.consumer import Consumer
from list_sync.consumer.writer import CsvWriter

writer = CsvWriter(filename='./output')
consumer = Consumer(
    callback=writer.write,
    group_id='my_group',
    topic_list=['wal_pg']
)

consumer.consume_messages()
```

## Testing

```bash
# Run test suite
poetry run python test/test_producer_pgsql.py
poetry run python test/test_producer_mysql.py
```


## Author

Stefano Babini (stefano.babini5@studio.unibo.it)

## License

MIT License