from carrot.connection import BrokerConnection
from carrot.messaging import Consumer

import requests
from datetime import datetime
import threading

from . import hardware

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

class LivePrinter(Printer):
    def __init__(self, printer, cash_drawer=None, *args, **kwargs):
        self.printer = printer
        self.cash_drawer = cash_drawer
        super(LivePrinter, self).__init__(*args, **kwargs)

    def message_received(self, message_data, message):
        message_type = message_data.get('print_type')
        if message_type == 'test':
            self.printer.do_print(message_data['text'])
            message.ack()
        elif message_type == 'ticket':
            self.printer.print_ticket(message_data['ticket'])
            message.ack()
        elif message_type == 'sales_report':
            self.printer.print_report(message_data['report_data'])
            message.ack()
        elif message_type == 'cash_drawer':
            if self.cash_drawer:
                self.cash_drawer.open()
            message.ack()
        else:
            print "Got unknown message_type", message_type
            message.reject()
