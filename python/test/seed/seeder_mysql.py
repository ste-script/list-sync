import mysql.connector
import sys
from base_seeder import seed_table

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='db',
    user='root',
    password='rootpassword',
    database='exampledb'
)

try:
    seed_table(conn)
except Exception as e:
    print(e, file=sys.stderr)
