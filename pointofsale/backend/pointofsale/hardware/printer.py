import string
import os.path

from django.utils.timezone import now


class TicketFormatter(object):
    def __init__(self, template_name, template_dir):
        template_name = template_name
        print "Loading template", template_name
        with open(os.path.join(template_dir, template_name), 'rb') as f:
            self.template = string.Template(f.read().decode('cp858'))

    def format_ticket(self, ticket):
        return self.template.substitute(self.build_dictionary(ticket))

    def build_dictionary(self, ticket):
        return ticket

    def format_report(self, events):
        header = """Imperial Cinema
Ticket Sales Report for %(today)s""" % {'today': now().strftime('%x')}

        sold_store = {}

        tickets_bit = ""
        total_exp_take = 0
        total_live_tickets = 0
        for event in events:
            event_sold_store = {}
            tickets_bit += event.name + "\n"
            tickets_bit += '-' * len(event.name) + "\n\n"

            total_tickets = 0
            total_ticket_take = 0

            max_name_len = max([len(n.name) for n in event.tickettype_set.all()])

            for ticket_type in event.tickettype_set.all():
                sold_live_tickets = ticket_type.tickets.filter(status='live').count()
                expected_take = sold_live_tickets * ticket_type.sale_price
                tickets_bit += "%(ticket_name)s: %(sold_live_tickets)s %(expected_take)0.2f\n" % {
                    'sold_live_tickets': str(sold_live_tickets).ljust(3),
                    'expected_take': expected_take,
                    'ticket_name': ticket_type.name.rjust(max_name_len)
                }

                total_tickets += sold_live_tickets
                total_ticket_take += expected_take

            tickets_bit += "\nTotal: %(sold_live_tickets)d tickets" \
                           "\n       %(expected_take)0.2f\n\n" % {
                'sold_live_tickets': total_tickets,
                'expected_take': total_ticket_take
            }
            total_exp_take += total_ticket_take
            total_live_tickets += total_tickets

            sold_store[event.name] = event_sold_store

        grand_total = "GRAND TOTAL: %(total_live_tickets)d tickets\n" \
                      "             %(total_take)0.2f\n" % {
            'total_live_tickets': total_live_tickets,
            'total_take': total_exp_take
        }

        return header + "\n\n" + tickets_bit + "\n\n" + grand_total

# This is vaguely what a TicketPrinter should look like
class TicketPrinter(object):
    def __init__(self, template_dir, template_name='basic.txt', **kwargs):
        self.template_name = template_name
        self.template_dir = template_dir
        self.formatters = {}
        self.report_formatter = TicketFormatter(template_name, template_dir)

    def do_print(self, data):
        print data

    def print_ticket(self, ticket):
        self.do_print(self.format_ticket(ticket))

    def formatter_for(self, template_name):
        formatter = self.formatters.get(template_name, None)
        if formatter is None:
            formatter = TicketFormatter(template_name=template_name, template_dir=self.template_dir)
            self.formatters[template_name] = formatter
        return formatter

    def format_ticket(self, ticket):
        template_name = self.template_name

        if ticket['print_template_extension'] != '':
            tn, dot, txt = template_name.rpartition('.')
            txt = ticket['print_template_extension'] + '.' + txt
            template_name = tn + dot + txt

        formatter = self.formatter_for(template_name)
        return formatter.format_ticket(ticket)

    def print_report(self, events):
        self.do_print(self.format_report(events))

    def format_report(self, events):
        return self.report_formatter.format_report(events)


class SerialTicketPrinter(TicketPrinter):
    def __init__(self, port, baudrate, before_report, after_report, **kwargs):
        import serial
        super(SerialTicketPrinter, self).__init__(**kwargs)
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate
        )
        self.before_report = before_report.decode('hex')
        self.after_report = after_report.decode('hex')

    def do_print(self, data):
        self.serial.write(data.encode('cp858'))

    def print_report(self, events):
        self.do_print(self.before_report)
        super(SerialTicketPrinter, self).print_report(events)
        self.do_print(self.after_report)


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
