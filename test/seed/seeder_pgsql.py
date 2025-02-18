import psycopg2
from .base_seeder import seed_table

# Connect to the MySQL database
conn = psycopg2.connect(
    host='db-pgsql',
    user='postgres',
    password='postgres',
    database='postgres'
)

def main():
    seed_table(conn)


if __name__ == '__main__':
    main()

