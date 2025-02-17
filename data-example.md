mysql
delete:
{"action": "D", "table": "example_table", "schema": "exampledb", "columns": [], "identity": [{"name": "id", "value": 42}, {"name": "category", "value": "old_cat"}, {"name": "domain", "value": "old.domain.test"}, {"name": "timestamp", "value": "2025-02-17T15:19:39"}], "pk": [{"name": "id", "value": 42}]}
insert
{"action": "I", "table": "example_table", "columns": [{"name": "id", "value": 999452}, {"name": "category", "value": "cat"}, {"name": "domain", "value": "cat.example.test"}, {"name": "timestamp", "value": "2025-02-17T15:36:33"}], "identity": [], "pk": [{"name": "id", "value": 999452}]}
update mysql
{"action": "U", "table": "example_table", "schema": "exampledb", "columns": [{"name": "id", "value": 999452}, {"name": "category", "value": "new_cat"}, {"name": "domain", "value": "new.example.test"}, {"name": "timestamp", "value": "2025-02-17T15:36:33"}], "identity": [{"name": "id", "value": 999452}, {"name": "category", "value": "cat"}, {"name": "domain", "value": "cat.example.test"}, {"name": "timestamp", "value": "2025-02-17T15:36:33"}], "pk": [{"name": "id", "value": 999452}]}

pgsql

delete
{"action":"D","table":"example_table","identity":[{"name":"id","value":3192}],"pk":[{"name":"id"}]}
insert
{"action":"I","table":"example_table","columns":[{"name":"id","value":999862},{"name":"category","value":"test"},{"name":"domain","value":"test.example.com"},{"name":"timestamp","value":"2025-02-17 16:38:38.660253"}],"pk":[{"name":"id"}]}
update
{"action":"U","table":"example_table","columns":[{"name":"id","value":999862},{"name":"category","value":"test"},{"name":"domain","value":"cat.example.com"},{"name":"timestamp","value":"2025-02-17 16:38:38.660253"}],"identity":[{"name":"id","value":999862}],"pk":[{"name":"id"}]}