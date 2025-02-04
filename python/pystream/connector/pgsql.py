import sys
import psycopg2
import psycopg2.extras
import json
from producer import send_message
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


def find_key(list, key_name='id'):
    for key in list:
        if key['name'] == key_name:
            return key['value']
    raise Exception("Key not found")


class DemoConsumer(object):
    def __call__(self, msg):
        try:
            payload = msg.payload
            # Extract the key from the payload
            json_value = json.loads(payload)
            key_name = json_value['pk'][0]['name']
            if 'columns' in json_value:
                key_value = find_key(json_value['columns'], key_name)
            elif 'identity' in json_value:
                key_value = find_key(json_value['identity'], key_name)
            else:
                raise Exception("Neither 'columns' nor 'identity' found in payload")
            key = str(key_value).encode('utf-8')
            # this ensures same row is sent to same partition avoiding out of order messages
            send_message(payload, key)
            msg.cursor.send_feedback(flush_lsn=msg.data_start)
        except Exception as e:
            print(f"Error processing message: {e}", file=sys.stderr)
            msg.cursor.send_feedback(flush_lsn=msg.data_start)


democonsumer = DemoConsumer()

print("Starting streaming, press Control-C to end...", file=sys.stderr)
try:
    # cur.execute("ALTER TABLE public.example_table REPLICA IDENTITY FULL;")
    cur.consume_stream(democonsumer)
except KeyboardInterrupt:
    cur.close()
    conn.close()
    print("The slot 'pytest' still exists. Drop it with "
          "SELECT pg_drop_replication_slot('pytest'); if no longer needed.",
          file=sys.stderr)
    print("WARNING: Transaction logs will accumulate in pg_xlog "
          "until the slot is dropped.", file=sys.stderr)
