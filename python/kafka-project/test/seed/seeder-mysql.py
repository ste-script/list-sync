import mysql.connector
import random
import string
from mysql.connector import Error
import time

start_time = time.time()

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='db',
    user='root',
    password='rootpassword',
    database='exampledb'
)
cur = conn.cursor()

def random_string(length):
    # Local binding for performance
    letters = string.ascii_lowercase
    return ''.join(random.choices(letters, k=length))

def seed_table():
    # Counters for diagnostics
    insert_count = 0
    update_count = 0
    delete_count = 0

    # Retrieve existing IDs once
    cur.execute("SELECT id FROM example_table")
    existing_ids = [row[0] for row in cur.fetchall()]

    # Increase the batch size to reduce commit overhead.
    batch_size = 1000

    # Batches for each type of operation
    insert_batch = []
    update_batch = []
    delete_batch = []

    total_iterations = 1_000_000

    # Pre-generate random actions.
    # Note: The original code gave twice as many chances for 'insert'
    actions = random.choices(['insert', 'update', 'insert', 'delete'], k=total_iterations)
    # Pre-generate random domain lengths for inserts only.
    # (We generate a list long enough; we won’t use more than needed.)
    domain_lengths = [random.randint(20, 50) for _ in range(total_iterations)]
    domain_length_index = 0

    for action in actions:
        if action == 'insert':
            category = random_string(5)
            # Use a pre-generated random length.
            dlen = domain_lengths[domain_length_index]
            domain_length_index += 1
            domain = random_string(dlen)
            insert_batch.append((category, domain))
            insert_count += 1

            if len(insert_batch) >= batch_size:
                cur.executemany(
                    "INSERT INTO example_table (category, domain) VALUES (%s, %s)",
                    insert_batch
                )
                insert_batch = []

        elif action == 'update':
            if existing_ids:
                # Swap-remove technique for O(1) removal.
                idx = random.randrange(len(existing_ids))
                existing_ids[idx], existing_ids[-1] = existing_ids[-1], existing_ids[idx]
                _id = existing_ids.pop()
                category = random_string(5)
                update_batch.append((category, _id))
                update_count += 1

                if len(update_batch) >= batch_size:
                    cur.executemany(
                        "UPDATE example_table SET category = %s WHERE id = %s",
                        update_batch
                    )
                    update_batch = []

        elif action == 'delete':
            if existing_ids:
                idx = random.randrange(len(existing_ids))
                existing_ids[idx], existing_ids[-1] = existing_ids[-1], existing_ids[idx]
                _id = existing_ids.pop()
                delete_batch.append((_id,))
                delete_count += 1

                if len(delete_batch) >= batch_size:
                    cur.executemany(
                        "DELETE FROM example_table WHERE id = %s",
                        delete_batch
                    )
                    delete_batch = []

    # Process any remaining operations in the batches.
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

    # Final commit (only one commit call here)
    conn.commit()
    seed_time = time.time() - start_time
    print(f"Inserted rows: {insert_count}")
    print(f"Updated rows: {update_count}")
    print(f"Deleted rows: {delete_count}")
    print (f"Time taken to seed the table: {seed_time:.2f} seconds")

try:
    seed_table()
finally:
    cur.close()
    conn.close()
