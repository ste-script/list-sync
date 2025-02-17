CREATE TABLE example_table (
  id BIGSERIAL PRIMARY KEY,
  category VARCHAR(30) NOT NULL,
  domain VARCHAR(50) NOT NULL DEFAULT '',
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on the domain column
CREATE INDEX domain_idx ON example_table (domain);
ALTER TABLE public.example_table REPLICA IDENTITY FULL;