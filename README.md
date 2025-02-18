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
## Quick Start
### 1. Prerequisites
```
# Enable network emulation (required for testing)
sudo ./load_module.sh
``` 
2. Start Services
```
# Start Kafka brokers
docker compose -f brokers.yml up -d

# Start PostgreSQL
docker compose -f pgsql.yml up -d

# Start MySQL
docker compose -f mysql.yml up -d
``` 
3. Start Consumers
``` 
# Start PostgreSQL consumers
docker compose -f pg-consumer.yml up -d

# Start MySQL consumers 
docker compose -f my-consumer.yml up -d
``` 
4. Run Tests
``` 
# Start seeder container
docker compose -f seeder.yml up -d

# Execute tests
 docker exec -it list-sync-seeder-1 poetry run python test/test_producer_pgsql.py
 docker exec -it list-sync-seeder-1 poetry run python test/test_producer_mysql.py
``` 
Configuration
Network Simulation
For testing with network latency:

Database Setup
MySQL: Uses row-based replication
PostgreSQL: Uses logical replication with wal2json
Testing Results
Consumer memory usage: ~98MB per instance
Test completion time: ~136 seconds
Data seeding time: ~60 seconds
JSON and Protobuf formats show similar performance
For more details, check the Python README.