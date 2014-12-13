from django.db import models
from model_utils import Choices

from . import utils


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
                pub.send({"print_type": "ticket", "ticket_id": ticket.id})

    def open_cash_drawer(self):
        with utils.get_printer_publisher(self.name) as pub:
            pub.send({"print_type": "cash_drawer"})
