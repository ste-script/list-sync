# list_sync

- [Stefano Babini](mailto:stefano.babini@studio.unibo.it)

## Abstract

list_sync is a Python-based system designed for Change Data Capture (CDC) from relational databases to Apache Kafka. It supports both MySQL and PostgreSQL as data sources, providing real-time streaming of database changes through a distributed system architecture while maintaining data consistency and fault tolerance.

## Concept

### Type of Product

- Library

### Use Cases

- Users are database administrators and system integrators
- Interaction is primarily through configuration and monitoring
- System runs continuously, capturing database changes in real-time
- Data is stored in Kafka topics and can be output to CSV files
- Multiple consumers can process the same data stream independently

## Requirements

### Functional Requirements

1. Capture database changes (inserts, updates, deletes) from MySQL and PostgreSQL
2. Stream changes to Kafka topics in real-time
3. Support multiple concurrent consumers
4. Output changes to CSV files
5. Support both batch processing and real-time streaming
6. The data produced to kafka need to use the same format from both databases

### Non-functional Requirements

1. Performance: Process 1 million rows in under 3 minutes
2. Scalability: Support multiple consumers per topic
3. Reliability: Handle network latency up to 800ms
4. Throughput: Support 20mbit/s bandwidth limitation

### Implementation Requirements

1. Python 3.12+ for connectors and consumers
2. Docker for containerization and deployment
3. Apache Kafka 3.9.0 for message streaming
4. MySQL with row-based replication
5. PostgreSQL with wal2json for logical replication

# Design

## Architecture

### Event-Driven Architecture

- Chosen for real-time change data capture and streaming requirements
- Enables loose coupling between producers (database connectors) and consumers
- Supports scalability through independent scaling of components
- Facilitates fault tolerance through message persistence and replay

Key benefits:

- Asynchronous processing
- Natural fit for database change events
- Easy scaling of consumers
- Built-in fault tolerance

## Infrastructure

### Components

1.  Database Servers

    - MySQL instance (row-based replication)
    - PostgreSQL instance (logical replication)
    - Each in separate containers

2.  Message Broker Cluster

    - 3 Kafka brokers in separate containers
    - Replication factor: 3
    - Number of partitions: 3

3.  Connectors

    - MySQL connector (CDC)
    - PostgreSQL connector (CDC)
    - Run as separate services

4.  Consumers

    - Multiple instances possible
    - Scale horizontally
    - CSV writers for output

### Network Distribution

#### Docker Network Isolation

- All components run in Docker containers on a dedicated bridge network (`list_sync-net`)
- Fixed IP addressing in `172.18.0.0/16` subnet
- Brokers assigned static IPs:
  - `broker1: 172.18.0.50`
  - `broker2: 172.18.0.51`
  - `broker3: 172.18.0.52`

#### Component Placement

- All services run on the same physical machine but in isolated containers
- Database servers:
  - MySQL container (`db-mysql`)
  - PostgreSQL container (`db-pgsql`)
- Message brokers:
  - 3 Kafka brokers in separate containers
  - Inter-broker latency simulated up to 300ms (600ms round-trip)
- Connectors:
  - MySQL connector container
  - PostgreSQL connector container
- Consumers:
  - Multiple consumer containers possible
  - Can scale horizontally up to cluster capacity

#### Network Characteristics

- Bandwidth limited to 20mbit/s between brokers
- Simulated network latency of 300ms between brokers
- All components communicate via Docker bridge network
- Service discovery via static hostnames in Docker DNS

### Service Discovery

- Static host names in Docker network
- Kafka brokers: broker1:9092, broker2:9094, broker3:9095
- MySQL: [db-mysql:3306](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)
- PostgreSQL: [db-pgsql:5432](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html)

## Modelling

### Domain Entities

1.  Connector

    - Continuously fetch changes from the databaes
    - Properties: database, table, kafka_conf

2.  Producer

    - Send the fetched data to the kafka cluster
    - Properties: topic, kafka_conf

3.  Consumer

    - Groups consumers for parallel processing
    - Properties: group ID, topic subscriptions

4.  Writer

    - Example writer to write the file into csv files
    - Properties: filename, consumer_id, split_files

### Domain Events

1.  Database Events

    - Insert (I)
    - Update (U)
    - Delete (D)

### State Information

- Database table state
- Kafka topic offsets
- Consumer group positions
- Replication slots (PostgreSQL)
- Binary log position (MySQL)

## Interaction

### Communication Patterns

1.  Database to Connector

    - MySQL: Binary log streaming
    - PostgreSQL: Logical replication protocol

2.  Connector to Kafka

    - Asynchronous message production
    - At-least-once delivery
    - Key-based partitioning
    - Compression

3.  Kafka to Consumer

    - Pull-based consumption
    - Batch processing support
    - Commit management

## Behaviour

### Component State Management

1.  Connectors

    - Stateful tracking of replication position
    - Maintains database connections
    - Buffers messages for batch sending

2.  Consumers

    - Stateful offset tracking
    - Manages CSV file handles
    - Handles group coordination

### State Updates

- Database changes trigger connector events
- Connectors update Kafka topics
- Consumers update CSV files
- Offset commits maintain progress

### Implementation

Key technologies used:

- Python 3.12
- Apache Kafka 3.9.0
- MySQL 8.0 with row-based replication
- PostgreSQL 16 with wal2json
- Docker and Docker Compose

### Testing Results

Hardware specifications:

```text
H/W path         Device         Class          Description
==========================================================
/0/0                            memory         15GiB System memory
/0/1                            processor      12th Gen Intel(R) Core(TM) i7-1280P
```

Performance metrics:

- Consumer memory usage: ~98MB per instance
- Test completion time (without latency): ~136 seconds
- Data seeding time: ~40 seconds
- Similar performance between JSON and Protobuf formats



## Deployment

1. Load network emulation module:

```bash
sudo ./load_module.sh
```

2. Start services:

```bash
docker compose -f brokers.yml -f pgsql.yml -f mysql.yml  up -d
```

3. (Optional) Start consumers:

```bash
docker compose -f pg-consumer.yml up -d
docker compose -f my-consumer.yml up -d
```

4. Run tests:

```bash
docker compose -f brokers.yml -f pgsql.yml -f mysql.yml -f seeder.yml  up -d
docker exec -it list-sync-seeder-1 poetry run python test/test_producer_pgsql.py
docker exec -it list-sync-seeder-1 poetry run python test/test_producer_mysql.py
```

## User Guide

## Installation

```bash
poetry install
```

## Quick Start

### Connector

```
from list_sync.connector.base_connector import Connector

# Using default values
default_connector = Connector()
default_connector.connect()

# Using custom configuration
custom_connector = Connector(
    db_type='mysql',
    host='localhost',
    port=3306,
    user='my_user',
    password='my_password',
    database='my_database',
    table='my_table',
    kafka_conf={
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'my-group'
    },
    topic=['my_topic']
)

# Connect to the database
custom_connector.connect()
```

### Consumer Usage

Multiple consumers can be initialized at the same time to pull from the same topic.
If two or more consumers have the same group_id, it is assured that each message will be processed by only one consumer in the group.

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

### Data and Consistency Issues

#### Data Storage

- MySQL and PostgreSQL databases store the source data
- Kafka topics store the change data capture events
- CSV files store the output from consumers

#### Test storage Implementation

- Relational databases with tables containing:
  - id (BIGINT/BIGSERIAL PRIMARY KEY)
  - category (VARCHAR)
  - domain (VARCHAR)
  - timestamp (TIMESTAMP)
- Indexed on domain column for performance

#### Query Patterns

- MySQL: Uses row-based replication to capture changes
- PostgreSQL: Uses wal2json for logical replication
- Both feed into Kafka topics for distribution

### Fault-Tolerance

#### Data Replication

- 3-node Kafka cluster with replication factor 3
- MySQL row-based replication
- PostgreSQL logical replication

#### Error Handling

- Consumer group management for failover
- Automatic retries in Kafka producers
- Transaction logs maintained in both databases

### Availability

#### Caching

- Kafka broker caching with configurable retention
- Consumer batch processing support

#### Load Balancing

- 3 Kafka brokers with automatic partition distribution
- Multiple consumer instances per group
- Configurable number of partitions (default 3)

#### Network Partitioning

- System maintains consistency with Kafka's partition leadership
- Tolerates network latency up to 800ms
- Handles bandwidth limitations of 20mbit/s

### Security

#### Authentication

- MySQL: Native password authentication for replication user
- PostgreSQL: Password authentication

#### Authorization

- MySQL: Specific grants for replication and table access
- PostgreSQL: Logical replication permissions

## Release

The project is organized into several modules:

- Database connectors (python/list_sync/connector)
- Consumer implementation (python/list_sync/consumer)

```bash
poetry install
```

## Self-evaluation

### Stefano Babini

#### Strengths

- Successfully implemented change data capture for both MySQL and PostgreSQL
- Achieved performance targets (1M rows < 3 minutes)
- Built scalable consumer architecture
- Comprehensive test coverage with realistic network conditions

#### Weaknesses

- More configuration options could be exposed
- Security features could be enhanced
- Monitoring and observability could be improved
