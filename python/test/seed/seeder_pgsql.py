import psycopg2
import sys
from base_seeder import seed_table

# Connect to the MySQL database
conn = psycopg2.connect(
    host='db',
    user='postgres',
    password='postgres',
    database='postgres'
)

try:
    seed_table(conn)
except Exception as e:
    print(e, file=sys.stderr)
