mysql

delete
{"action":"D","table":"example_table","pk":[{"name":"id"}],"identity":[{"name":"id","value":48},{"name":"category","value":"qrlwz"},{"name":"domain","value":"yheusiahrapzdmtbjorkhalpdpcmsz"},{"name":"timestamp","value":"2025-02-17T15:19:39"}],"columns":[]}

insert
{"action":"I","table":"example_table","pk":[{"name":"id"}],"identity":[],"columns":[{"name":"id","value":999453},{"name":"category","value":"cat"},{"name":"domain","value":"test.example.test"},{"name":"timestamp","value":"2025-02-17T15:52:25"}]}

update
{"action":"U","table":"example_table","pk":[{"name":"id"}],"identity":[{"name":"id","value":999453},{"name":"category","value":"cat"},{"name":"domain","value":"test.example.test"},{"name":"timestamp","value":"2025-02-17T15:52:25"}],"columns":[{"name":"id","value":999453},{"name":"category","value":"new_cat"},{"name":"domain","value":"new.example.test"},{"name":"timestamp","value":"2025-02-17T15:52:25"}]}


pgsql
delete
{"action":"D","table":"example_table","identity":[{"name":"id","value":3192}],"pk":[{"name":"id"}]}
insert
{"action":"I","table":"example_table","columns":[{"name":"id","value":999862},{"name":"category","value":"test"},{"name":"domain","value":"test.example.com"},{"name":"timestamp","value":"2025-02-17 16:38:38.660253"}],"pk":[{"name":"id"}]}
update
{"action":"U","table":"example_table","columns":[{"name":"id","value":999862},{"name":"category","value":"test"},{"name":"domain","value":"cat.example.com"},{"name":"timestamp","value":"2025-02-17 16:38:38.660253"}],"identity":[{"name":"id","value":999862}],"pk":[{"name":"id"}]}