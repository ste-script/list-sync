import sys
import psycopg2
import psycopg2.extras
import json
from producer import send_message
conn = psycopg2.connect('dbname=postgres user=postgres password=postgres host=pgsql',
                        connection_factory=psycopg2.extras.LogicalReplicationConnection)
cur = conn.cursor()
replication_options = {
    "add-tables": "public.example_table",
    "format-version": "2",
    "include-schemas": "false",
    "include-types": "false",
    "include-transaction": "false",
}
try:
    # test_decoding produces textual output
    cur.start_replication(slot_name='pytest', decode=True,
                          options=replication_options)
except psycopg2.ProgrammingError:
    cur.create_replication_slot('pytest', output_plugin='wal2json')
    cur.start_replication(slot_name='pytest', decode=True,
                          options=replication_options)


class DemoConsumer(object):
    def __call__(self, msg):
        payload = msg.payload
        if payload.startswith('BEGIN'):
            print("Transaction started")
        elif payload.startswith('COMMIT'):
            print("Transaction committed")
        else:
            print(json.loads(payload))
            send_message(payload)
        msg.cursor.send_feedback(flush_lsn=msg.data_start)


democonsumer = DemoConsumer()

print("Starting streaming, press Control-C to end...", file=sys.stderr)
try:
    cur.consume_stream(democonsumer)
except KeyboardInterrupt:
    cur.close()
    conn.close()
    print("The slot 'pytest' still exists. Drop it with "
          "SELECT pg_drop_replication_slot('pytest'); if no longer needed.",
          file=sys.stderr)
    print("WARNING: Transaction logs will accumulate in pg_xlog "
          "until the slot is dropped.", file=sys.stderr)
