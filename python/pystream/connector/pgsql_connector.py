import sys
import psycopg2
import psycopg2.extras
import json
from pystream.connector.producer import send_message
conn = psycopg2.connect('dbname=postgres user=postgres password=postgres host=db',
                        connection_factory=psycopg2.extras.LogicalReplicationConnection)
cur = conn.cursor()
replication_options = {
    "add-tables": "public.example_table",
    "format-version": "2",
    "include-schemas": "false",
    "include-types": "false",
    "include-transaction": "false",
    "include-pk": "true"
}
try:
    # test_decoding produces textual output
    cur.start_replication(slot_name='pytest', decode=True,
                          options=replication_options)
except psycopg2.ProgrammingError:
    cur.create_replication_slot('pytest', output_plugin='wal2json')
    cur.start_replication(slot_name='pytest', decode=True,
                          options=replication_options)


def find_key(lst, key_name='id'):
    try:
        return next(key['value'] for key in lst if key['name'] == key_name)
    except StopIteration:
        raise KeyError(f"Key '{key_name}' not found")


class DemoConsumer(object):
    def __call__(self, msg):
        try:
            payload = msg.payload
            json_value = json.loads(payload)

            key_name = json_value['pk'][0]['name']
            key_sources = ('columns', 'identity')

            for source in key_sources:
                if source in json_value:
                    key_value = find_key(json_value[source], key_name)
                    break
            else:
                raise KeyError(
                    "Neither 'columns' nor 'identity' found in payload")

            key = str(key_value).encode('utf-8')
            send_message(payload, key)

        except Exception as e:
            print(f"Error processing message: {e}", file=sys.stderr)

        finally:
            msg.cursor.send_feedback(flush_lsn=msg.data_start)


democonsumer = DemoConsumer()

print("Starting streaming, press Control-C to end...", file=sys.stderr)
try:
    # cur.execute("ALTER TABLE public.example_table REPLICA IDENTITY FULL;")
    cur.consume_stream(democonsumer)
except KeyboardInterrupt:
    print("The slot 'pytest' still exists. Drop it with "
          "SELECT pg_drop_replication_slot('pytest'); if no longer needed.",
          file=sys.stderr)
    print("WARNING: Transaction logs will accumulate in pg_xlog "
          "until the slot is dropped.", file=sys.stderr)
finally:
    cur.close()
    conn.close()
