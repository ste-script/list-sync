import psycopg2
import psycopg2.extras

conn = psycopg2.connect('dbname=postgres user=postgres password=postgres host=pgsql')


#insert 10000 rows/sec into the table and exit after ten seconds

cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS public.newtable (id serial PRIMARY KEY, text varchar);')
conn.commit()
dummmy_data = "Hello, World!"
i = 0
while True:
    try:
        cur.extras.execute_values(cur, 'INSERT INTO public.newtable (text) VALUES %s', [(dummmy_data,)]*100)
        conn.commit()
        i += 1
        if i % 100 == 0:
            print(f"Inserted {i*100} rows")
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Failed to insert data: {e}")
        break
    if i == 100:
        break
conn.commit()
conn.close()