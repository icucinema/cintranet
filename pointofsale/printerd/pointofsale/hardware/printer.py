import string
import os.path

from django.utils.timezone import now

from jinja2 import FileSystemLoader, Environment
from ticketml.ticketml import TicketML, Ibm4610Backend, CbmBackend
import datetime

BACKENDS = {
        'ibm4610': Ibm4610Backend,
        'cbm': CbmBackend,
}


# This is vaguely what a TicketPrinter should look like
class TicketPrinter(object):
    def __init__(self, template_dir, **kwargs):
        self.template_dir = template_dir
        self.environment = Environment(loader=FileSystemLoader(template_dir))

    def do_print(self, data):
        data.go({}, self.backend)

    def print_ticket(self, ticket):
        self.do_print(self.format_ticket(ticket))

    def format_ticket(self, ticket, pte_default='basic', add_ticket_attributes=True):
        template_fn = ticket.get('print_template_extension', pte_default)
        print 'Loading template', template_fn
        template = self.environment.get_template(template_fn + '.xml')

        if add_ticket_attributes:
            ticket['timestamp'] = datetime.datetime.fromtimestamp(ticket['timestamp'])
            ticket['ticket_type_price'] = '{:.2f}'.format(ticket['ticket_type_price'])

        ticketdata = template.render(ticket).split('\n')
        print [ln.lstrip() for ln in ticketdata]
        ticket_output = u'\n'.join([ln.lstrip() for ln in ticketdata])

        return TicketML.parse(ticket_output)

    def print_report(self, events):
        self.do_print(self.format_report(events))

    def format_report(self, events):
        return 'nope'

    def print_head(self, head):
        self.do_print(self.format_ticket(head, 'head', False))


class SerialTicketPrinter(TicketPrinter):
    def __init__(self, port, baudrate, backend_name, **kwargs):
        import serial
        super(SerialTicketPrinter, self).__init__(**kwargs)
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate
        )
        self.backend = BACKENDS[backend_name](self.serial)


class LoggingTicketPrinter(TicketPrinter):
    def __init__(self, ticketprinter, logger, **kwargs):
        self.logger = logger
        self.wrapped_printer = ticketprinter

        super(LoggingTicketPrinter, self).__init__(**kwargs)

    def print_ticket(self, ticket):
        self.wrapped_printer.print_ticket(ticket)

        super(LoggingTicketPrinter, self).print_ticket(ticket)

    def format_ticket(self, ticket):
        output = ','.join(map(str, [
            ticket['film_title'],
            ticket['date'],
            ticket['time'],
            ticket['type'],
            ticket['price'],
            ticket['id']
        ]))
        self.logger.info("Printing ticket " + output)
