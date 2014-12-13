from carrot.connection import BrokerConnection
from carrot.messaging import Consumer

import requests
from datetime import datetime
import threading

config = {
    'printer': {
        'name': 'test_printer',
        'registry': 'http://localhost:8000/pointofsale/printers/',
        'auth_token': '',
        'id': 1,
    },
    'broker': {
        'hostname': 'localhost',
        'port': 5672,
        'userid': 'cintranet',
        'password': 'cintranet',
        'virtual_host': '/cintranet',
    },
}

class PrinterRegistry(object):
    def __init__(self, url, auth_token):
        self.url = url
        self.sess = requests.session()
        self.sess.headers['Authorization'] = 'Token {}'.format(auth_token)

    def now(self):
        return datetime.now().isoformat()

    def register(self, name):
        resp = self.sess.post(self.url, data={'name': name, 'last_seen': self.now()})
        resp.raise_for_status()
        return resp.json()

    def lookup(self, id):
        resp = self.sess.get(self.url + '{}/'.format(id))
        resp.raise_for_status()
        return resp.json()

    def find_by_name(self, name):
        resp = self.sess.get(self.url, params={'name': name})
        resp.raise_for_status()
        j = resp.json()
        if j['count'] == 1:
            return j['results'][0]
        return None

    def ping(self, id):
        resp = self.sess.patch(self.url + '{}/'.format(id), data={'last_seen': self.now()})
        resp.raise_for_status()
        return resp.json()

class PrinterMessageThread(threading.Thread):
    def __init__(self, printer):
        super(PrinterMessageThread, self).__init__()
        self.printer = printer
        self.daemon = True

    def run(self):
        self.printer.consumer.wait()

class Printer(object):
    def __init__(self, name, registry, amqp_connection):
        self.name = name
        self.registry = registry
        self._register()
        self._setup_amqp(amqp_connection)

    def _register(self):
        self.data = self.registry.find_by_name(self.name)
        if self.data:
            self.data = self.registry.ping(self.data['id'])
        else:
            self.data = self.registry.register(self.name)

        print "Running as printer", self.data['id']

    def _setup_amqp(self, conn):
        self.consumer = Consumer(connection=conn, exchange="printer", queue="printer.{}".format(self.data['name']), routing_key=self.data['name'])
        self.consumer.register_callback(lambda message_data, message: self.message_received(message_data, message))

    def message_received(self, message_data, message):
        raise Exception("'message_received' must be implemented!")

class TestPrinter(Printer):
    def message_received(self, message_data, message):
        print "Got message", message_data
        message.ack()

conn = BrokerConnection(**config['broker'])

registry = PrinterRegistry(config['printer']['registry'], config['printer']['auth_token'])
printer = TestPrinter(config['printer']['name'], registry, conn)
pm_handler = PrinterMessageThread(printer)

pm_handler.start()
while True:
  pm_handler.join(1)
  if not pm_handler.is_alive():
    break
