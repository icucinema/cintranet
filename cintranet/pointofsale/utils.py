from carrot.connection import DjangoBrokerConnection
from carrot.messaging import Publisher

def get_amqp_connection():
    return DjangoBrokerConnection()

def get_printer_publisher(name):
    return contextlib.closing(Publisher(connection=conn, exchange="printer", routing_key=name))
