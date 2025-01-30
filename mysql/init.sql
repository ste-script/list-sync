CREATE TABLE example_table (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  category VARCHAR(30) NOT NULL,
  domain VARCHAR(50) NOT NULL DEFAULT '',
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on the domain column
CREATE INDEX domain_idx ON example_table (domain);

CREATE USER 'repl_user'@'%' IDENTIFIED BY 'repl_password';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'repl_user'@'%';
GRANT REPLICATION SLAVE, SELECT ON *.* TO 'repl_user'@'%';
GRANT SELECT ON exampledb.example_table TO 'repl_user'@'%';