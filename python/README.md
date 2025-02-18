List-Sync
A Python library for synchronizing database changes through Apache Kafka using Change Data Capture (CDC).

Features
Change Data Capture (CDC) support for MySQL and PostgreSQL
Real-time streaming of database changes to Kafka topics
Scalable consumers with CSV output
Support for Insert, Update, and Delete operations
Network latency simulation for testing
JSON message format compatibility
Installation
Quick Start
Start the required services:
Start the producers:
Start the consumers:
Testing
Run the test suite:

Performance Metrics
Consumer Memory Usage: ~98MB per instance
Test Completion Time: ~136 seconds
Data Seeding Time: ~60 seconds
Message Format: JSON (equivalent performance to Protobuf)
Configuration
Network Simulation
Kafka Configuration
Bootstrap Servers: broker1:9092
Compression: lz4
Batch Size: 100MB
Batch Messages: 1,000,000
Replication Factor: 3
Partitions: 3
Project Structure
connector/: Database connectors
mysql_connector.py: MySQL CDC implementation
pgsql_connector.py: PostgreSQL CDC implementation
consumer/: Kafka consumer implementation
writer/: Output writers
test/: Test suite and seeding utilities
License
MIT License

Author
Stefano Babini (stefano.babini5@studio.unibo.it)