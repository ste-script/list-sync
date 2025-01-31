import mysql.connector
import random
import string
from mysql.connector import Error

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='db',
    user='root',
    password='rootpassword',
    database='exampledb'
)
cur = conn.cursor(prepared=True)

def random_string(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def execute_batch_insert(cursor, sql, data, batch_size=1000):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        cursor.executemany(sql, batch)

def seed_table():
    insert_count = 0
    update_count = 0
    delete_count = 0

    # Retrieve existing IDs
    cur.execute("SELECT id FROM example_table")
    existing_ids = [row[0] for row in cur.fetchall()]

    batch_size = 1000
    insert_batch = []
    update_batch = []
    delete_batch = []

    for _ in range(1000000):
        action = random.choice(['insert', 'update', 'insert', 'delete'])
        if action == 'insert':
            category = random_string(5)
            domain = random_string(random.randint(20, 50))
            insert_batch.append((category, domain))
            insert_count += 1

            if len(insert_batch) >= batch_size:
                cur.executemany(
                    "INSERT INTO example_table (category, domain) VALUES (%s, %s)",
                    insert_batch
                )
                conn.commit()
                insert_batch = []

        elif action == 'update':
            if existing_ids:
                idx = random.randrange(len(existing_ids))
                existing_ids[idx], existing_ids[-1] = existing_ids[-1], existing_ids[idx]
                id = existing_ids.pop()
                category = random_string(5)
                update_batch.append((category, id))
                update_count += 1

                if len(update_batch) >= batch_size:
                    cur.executemany(
                        "UPDATE example_table SET category = %s WHERE id = %s",
                        update_batch
                    )
                    conn.commit()
                    update_batch = []

        elif action == 'delete':
            if existing_ids:
                idx = random.randrange(len(existing_ids))
                existing_ids[idx], existing_ids[-1] = existing_ids[-1], existing_ids[idx]
                id = existing_ids.pop()
                delete_batch.append((id,))
                delete_count += 1

                if len(delete_batch) >= batch_size:
                    cur.executemany(
                        "DELETE FROM example_table WHERE id = %s",
                        delete_batch
                    )
                    conn.commit()
                    delete_batch = []

    # Process remaining batches
    if insert_batch:
        cur.executemany(
            "INSERT INTO example_table (category, domain) VALUES (%s, %s)",
            insert_batch
        )
    if update_batch:
        cur.executemany(
            "UPDATE example_table SET category = %s WHERE id = %s",
            update_batch
        )
    if delete_batch:
        cur.executemany(
            "DELETE FROM example_table WHERE id = %s",
            delete_batch
        )

    conn.commit()
    print(f"Inserted rows: {insert_count}")
    print(f"Updated rows: {update_count}")
    print(f"Deleted rows: {delete_count}")

try:
    seed_table()
finally:
    cur.close()
    conn.close()