import contextlib
import redis
import json

class Publisher(object):
    def __init__(self, conn, name):
        self.conn = conn
        self.name = name

    def send(self, obj):
        print "pushing", obj, "into", self.name
        self.conn.lpush('printer.{}'.format(self.name), json.dumps(obj))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False

def get_connection():
    return redis.StrictRedis.from_url('redis://localhost/0')

def get_printer_publisher(name, conn=None):
    if conn is None:
        conn = get_connection()
    return Publisher(conn, name)
