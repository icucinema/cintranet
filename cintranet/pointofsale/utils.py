from carrot.connection import DjangoBrokerConnection
from carrot.messaging import Publisher

import contextlib

def get_amqp_connection():
    return DjangoBrokerConnection()

def get_printer_publisher(name, conn=None):
    if conn is None:
        conn = get_amqp_connection()
    return contextlib.closing(Publisher(connection=conn, exchange="printer", routing_key=name))
