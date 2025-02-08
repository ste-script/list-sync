import mysql.connector
from .base_seeder import seed_table

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='rootpassword',
    database='exampledb'
)


def main():
    try:
        seed_table(conn)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
