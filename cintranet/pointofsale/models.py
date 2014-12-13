from django.db import models
from model_utils import Choices

from . import utils

def _format_ticket_for_printer(ticket):
    return {
        'header': str(ticket.ticket_position_in_showing()).zfill(3),
        'ticket_head': 'Imperial Cinema Presents',
        'film_title': ticket.ticket_type.event.name,
        'film_line2': '',
        'film_line3': '',
        'date': ticket.ticket_type.event.start_time.strftime('%x'),
        'time': ticket.ticket_type.event.start_time.strftime('%X'),
        'type': ticket.ticket_type.name,
        'price': str(ticket.ticket_type.sale_price),
        'id': ticket.printed_id(),
        'number': str(ticket.ticket_position_in_showing()).zfill(3),
        'website': 'www.imperialcinema.co.uk',
        'tagline': 'Sponsored by',
        'ticket_uid': '%d' % (ticket.pk),
        'print_template_extension': ticket.ticket_type.print_template_extension,
    }


class Printer(models.Model):
    name = models.CharField(max_length=256, null=False, default=False, unique=True)
    last_seen = models.DateTimeField(null=False)

    def print_test_page(self):
        with utils.get_printer_publisher(self.name) as pub:
            pub.send({"print_type": "test", "text": "This is a test of the printer setup. If this is printed successfully and in full, then the connection between Django and this printer is working successfully."})

    def print_ticket(self, ticket):
        self.print_tickets([ticket])

    def print_tickets(self, tickets):
        with utils.get_printer_publisher(self.name) as pub:
            for ticket in tickets:
                pub.send({"print_type": "ticket", "ticket_id": ticket.id, 'ticket': _format_ticket_for_printer(ticket)})

    def open_cash_drawer(self):
        with utils.get_printer_publisher(self.name) as pub:
            pub.send({"print_type": "cash_drawer"})
