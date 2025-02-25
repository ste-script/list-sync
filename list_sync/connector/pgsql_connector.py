import sys
import psycopg2
import psycopg2.extras
import json
from list_sync.connector.producer import Producer

_default_conf = {
    "host": "db-pgsql",
    "port": "5432",
    "user": "postgres",
    "passwd": "postgres",
    "database": "postgres",
    "table": "example_table",
}


class PgsqlConnector:
    def __init__(self, conf: dict[str, str] = _default_conf, topic: dict[str] = ['wal']):
        self.host = conf.get('host')
        self.port = conf.get('port')
        self.user = conf.get('user')
        self.password = conf.get('passwd')
        self.database = conf.get('database')
        self.table = conf.get('table')
        wal2jsonConf = {"format-version": "2",
                        "include-schemas": "false",
                        "include-types": "false",
                        "include-transaction": "false",
                        "include-pk": "true"}
        wal2jsonConf["add-tables"] = f"public.{self.table}"
        self.pgsqlConf = wal2jsonConf
        self.consumer = WalConsumer(conf.get('kafka_conf', False), topic)

    def connect(self):
        self.connection = psycopg2.connect(f'dbname={self.database} user={self.user} password={self.password} host={self.host}',
                                           connection_factory=psycopg2.extras.LogicalReplicationConnection)
        self.cur = self.connection.cursor()
        try:
            self.cur.start_replication(slot_name='pytest', decode=True,
                                       options=self.pgsqlConf)
        except psycopg2.ProgrammingError:
            self.cur.create_replication_slot(
                'pytest', output_plugin='wal2json')
            self.cur.start_replication(slot_name='pytest', decode=True,
                                       options=self.pgsqlConf)
        print("Starting streaming, press Control-C to end...", file=sys.stderr)
        try:
            self.cur.consume_stream(self.consumer)
        except KeyboardInterrupt:
            print("The slot 'pytest' still exists. Drop it with "
                  "SELECT pg_drop_replication_slot('pytest'); if no longer needed.",
                  file=sys.stderr)
            print("WARNING: Transaction logs will accumulate in pg_xlog "
                  "until the slot is dropped.", file=sys.stderr)
        finally:
            self.cur.close()
            self.connection.close()


class WalConsumer(object):
    def __init__(self, kakfa_conf=False, topic=['wal']):
        if not kakfa_conf:
            print(
                "No Kafka configuration provided, using default configuration", file=sys.stderr)
            self.producer = Producer(topic=topic)
        else:
            self.producer = Producer(kakfa_conf, topic)

    def find_key(self, lst, key_name='id'):
        try:
            return next(key['value'] for key in lst if key['name'] == key_name)
        except StopIteration:
            raise KeyError(f"Key '{key_name}' not found")

    def __call__(self, msg):
        try:
            payload = msg.payload
            json_value = json.loads(payload)

            key_name = json_value['pk'][0]['name']
            key_sources = ('columns', 'identity')

            for source in key_sources:
                if source in json_value:
                    key_value = self.find_key(json_value[source], key_name)
                    break
            else:
                raise KeyError(
                    "Neither 'columns' nor 'identity' found in payload")

            key = str(key_value).encode('utf-8')
            self.producer.send_message(payload, key)

        except Exception as e:
            print(f"Error processing message: {e}", file=sys.stderr)

        finally:
            msg.cursor.send_feedback(flush_lsn=msg.data_start)


if __name__ == '__main__':
    m = PgsqlConnector(topic=['wal_pg'])
    m.connect()
