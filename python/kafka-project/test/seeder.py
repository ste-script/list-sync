import psycopg2
import random
import string
from psycopg2.extras import execute_values, execute_batch

# Connect to the PostgreSQL database
conn = psycopg2.connect('dbname=postgres user=postgres password=postgres host=pgsql')
cur = conn.cursor()

# Function to generate random strings
def random_string(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Function to seed the table with random data
def seed_table():
    insert_count = 0
    update_count = 0
    delete_count = 0

    # Retrieve existing IDs and optimize for O(1) deletions
    cur.execute("SELECT id FROM example_table")
    existing_ids = [row[0] for row in cur.fetchall()]

    batch_size = 1000  # Adjust batch size based on testing
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
                execute_values(
                    cur,
                    "INSERT INTO example_table (category, domain) VALUES %s",
                    insert_batch,
                    template="(%s, %s)",
                    page_size=batch_size
                )
                conn.commit()
                insert_batch = []

        elif action == 'update':
            idx = random.randrange(len(existing_ids))
            existing_ids[idx], existing_ids[-1] = existing_ids[-1], existing_ids[idx]
            id = existing_ids.pop()
            category = random_string(5)
            update_batch.append((category, id))
            update_count += 1

            if len(update_batch) >= batch_size:
                execute_batch(
                    cur,
                    "UPDATE example_table SET category = %s WHERE id = %s",
                    update_batch,
                    page_size=batch_size
                )
                conn.commit()
                update_batch = []

        elif action == 'delete':
            if existing_ids:
                # Efficient O(1) deletion using swap-and-pop
                idx = random.randrange(len(existing_ids))
                existing_ids[idx], existing_ids[-1] = existing_ids[-1], existing_ids[idx]
                id = existing_ids.pop()
                delete_batch.append((id,))
                delete_count += 1

                if len(delete_batch) >= batch_size:
                    execute_batch(
                        cur,
                        "DELETE FROM example_table WHERE id = %s",
                        delete_batch,
                        page_size=batch_size
                    )
                    conn.commit()
                    delete_batch = []

    # Process remaining batches
    if insert_batch:
        execute_values(
            cur,
            "INSERT INTO example_table (category, domain) VALUES %s",
            insert_batch,
            template="(%s, %s)",
            page_size=len(insert_batch)
        )
    if update_batch:
        execute_batch(
            cur,
            "UPDATE example_table SET category = %s WHERE id = %s",
            update_batch,
            page_size=len(update_batch)
        )
    if delete_batch:
        execute_batch(
            cur,
            "DELETE FROM example_table WHERE id = %s",
            delete_batch,
            page_size=len(delete_batch)
        )

    conn.commit()
    print(f"Inserted rows: {insert_count}")
    print(f"Updated rows: {update_count}")
    print(f"Deleted rows: {delete_count}")

# Seed the table
seed_table()

# Close the database connection
cur.close()
conn.close()