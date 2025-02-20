# List-Sync

A Python-based system for streaming database changes (MySQL and PostgreSQL) to Apache Kafka using Change Data Capture (CDC).

## Overview

This project provides a solution for:

- Capturing database changes (inserts, updates, deletes) from MySQL and PostgreSQL
- Streaming these changes to Kafka topics
- Consuming and processing the change events
- Writing the changes to CSV files

## Architecture

- Database Connectors: Support for MySQL (mysql_connector.py) and PostgreSQL (pgsql_connector.py)
- Kafka Infrastructure: 3-node Kafka cluster with replication
- Consumers: Scalable consumer implementation with CSV output capability

## Database Setup Info

MySQL: Uses row-based replication
PostgreSQL: Uses logical replication with wal2json

## Quick Start

### 1. Prerequisites

Load the sch_netem kernel module to use traffic control (tc) to simulate real use-case scenario with 20mbit/s bandwith limit and delay 300ms (so between brokers is 300+300 = 600ms)

```
# Enable network emulation
sudo ./load_module.sh
```

1. Start Services

```
# Start Kafka brokers
docker compose -f brokers.yml up -d

# Start PostgreSQL
docker compose -f pgsql.yml up -d

# Start MySQL
docker compose -f mysql.yml up -d
```

(optional) run
`sudo ./add_latency.sh`
to add latency also between brokers

2. (Optional) Start Consumers

> warning: if you strart consumers, the data consumed will be written into /python/test/data

Each consumer container has limited bandwith 20mbit/s and latency set to 800ms by default to simulate pessimistic scenario

```
# Start PostgreSQL consumers
docker compose -f pg-consumer.yml up -d

# Start MySQL consumers
docker compose -f my-consumer.yml up -d
```

### 2. Run Tests

The test will create the topic, seed the database with one million rows fake data and consume that to verify the transmission

```
# Start seeder container
docker compose -f seeder.yml up -d

# Execute tests
 docker exec -it list-sync-seeder-1 poetry run python test/test_producer_pgsql.py
 docker exec -it list-sync-seeder-1 poetry run python test/test_producer_mysql.py
```

## Testing Results

Hardware spec:

```
H/W path         Device         Class          Description
==========================================================
/0/0                            memory         15GiB System memory
/0/1                            processor      12th Gen Intel(R) Core(TM) i7-1280P
```

Consumer memory usage: ~98MB per instance
Test completion time (without additional latency): ~136 seconds
Data seeding time: ~60 seconds
Executed test with both json and protobuf, both showed similar performances in this scenario.
For more details, check the Python README.
