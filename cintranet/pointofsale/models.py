from django.db import models
from django.utils import timezone
from model_utils import Choices

import time
import random
from collections import namedtuple

from . import utils

Q = models.Q

def _pick_random_quotation():
    valid_quotations = FilmQuotation.objects.filter(enabled=True).filter((Q(valid_from=None) | Q(valid_from__lte=timezone.now())) & (Q(valid_to=None) | Q(valid_to__gte=timezone.now())))
    valid_quotation_ids = valid_quotations.values_list('id', flat=True)
    return FilmQuotation.objects.get(id=random.choice(valid_quotation_ids))

def _format_ticket_for_printer(ticket):
    try:
        quotation = _pick_random_quotation()
    except:
        quotation = namedtuple('QuotationMock', ['quotation', 'film_title'])(None, None)

    return {
        'film_title': ticket.ticket_type.event.name,
#        'ticket_number': str(ticket.ticket_position_in_showing()).zfill(3),
        'ticket_number': ticket.id,
        'timestamp': time.mktime(ticket.ticket_type.event.start_time.timetuple()),
        'ticket_type_name': ticket.ticket_type.name,
        'ticket_type_price': float(ticket.ticket_type.sale_price),
        'film_quote': quotation.quotation,
        'film_quote_film': quotation.film_title,
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


class FilmQuotation(models.Model):
    quotation = models.CharField(max_length=120, blank=False, null=False)
    film_title = models.CharField(max_length=120, blank=False, null=False)

    added_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    added_by = models.CharField(max_length=120, blank=False, null=False)
    enabled = models.BooleanField(default=True, blank=False)

    valid_from = models.DateTimeField(default=timezone.now, null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)

    def usable(self):
        is_usable = self.enabled
        is_usable = is_usable and (self.valid_from is None or timezone.now() >= self.valid_from)
        is_usable = is_usable and (self.valid_to is None or timezone.now() <= self.valid_to)
        return is_usable
    usable.boolean = True

    def __str__(self):
        r = ""
        if not self.usable():
            r = "[not in use] "
        return "{}{} [{}]".format(r, self.quotation.encode('utf-8'), self.film_title.encode('utf-8'))
