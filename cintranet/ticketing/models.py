import itertools

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now

from model_utils.managers import InheritanceManager
from model_utils.fields import StatusField
from model_utils import Choices

class Punter(models.Model):
    STATUS = Choices('full', 'associate', 'public')

    punter_type = StatusField(db_index=True)
    name = models.CharField(max_length=256, default="", null=False, blank=True)
    cid = models.CharField(max_length=16, default="", null=False, blank=True)
    login = models.CharField(max_length=16, default="", null=False, blank=True)
    swipecard = models.CharField(max_length=64, default="", null=False, blank=True)
    email = models.EmailField(max_length=256, default="", null=False, blank=True)
    comment = models.TextField(null=False, default="", blank=True)

    def __unicode__(self):
        return self.name

class Film(models.Model):
    name = models.CharField(max_length=256, default="", null=False, blank=False)
    description = models.TextField(default="", null=False, blank=True)
    picture = models.ImageField(blank=True, upload_to="film_banners")

    def __unicode__(self):
        return self.name

class Showing(models.Model):
    name = models.CharField(max_length=300, default="", null=False, blank=False)
    film = models.ForeignKey(Film, null=False, blank=False)
    start_time = models.DateTimeField(null=False, blank=False)

    def __unicode__(self):
        return u"{} ({})".format(self.name, self.start_time)

class EventType(models.Model):
    name = models.CharField(max_length=128, default="", null=False, blank=False)

    def __unicode__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=300, default="", null=False, blank=False)
    start_time = models.DateTimeField(null=False, blank=False)
    showings = models.ManyToManyField(Showing, null=False, related_name='events')
    event_types = models.ManyToManyField(EventType, null=True, related_name='event_types')

    def create_ticket_types_by_event_types(self):
        event_types = self.event_types.prefetch_related('ticket_templates').all()
        ticket_templates = [z.ticket_templates.all() for z in event_types]
        ticket_templates = itertools.chain.from_iterable(ticket_templates)
        for ticket_template in ticket_templates:
            TicketType.from_template(ticket_template, self).save()

    def __unicode__(self):
        return u"{} ({})".format(self.name, self.start_time)

class BaseTicketInfo(models.Model):
    online_description = models.TextField(null=False, default="", blank=True)
    sell_online = models.BooleanField(default=False)
    sell_on_the_door = models.BooleanField(default=True)
    general_availability = models.BooleanField(default=False)
    sale_price = models.DecimalField(
        decimal_places=2, max_digits=5,
        help_text='This is the price at which tickets are sold - the price punters will pay'
    )
    box_office_return_price = models.DecimalField(
        decimal_places=2, max_digits=5,
        help_text="""This is the ex-VAT price reported on the BOR for each film!"""
    )

    objects = InheritanceManager()

class TicketTemplate(BaseTicketInfo):
    event_type = models.ManyToManyField(EventType, related_name='ticket_templates')
    name = models.CharField(max_length=128, null=False, blank=False)

    def __unicode__(self):
        return self.name

class TicketType(BaseTicketInfo):
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=128, null=False, blank=False)

    template = models.ForeignKey(TicketTemplate, blank=True, null=True)

    def __unicode__(self):
        return u"{} (for {})".format(self.name, unicode(self.event))

    @classmethod
    def from_template(cls, template, event):
        props = (
            'online_description',
            'sell_online',
            'sell_on_the_door',
            'general_availability',
            'sale_price',
            'box_office_return_price'
        )
        tt = cls(
            template=template,
            event=event
        )
        tt.name = '{} for {}'.format(template.name, event.name)
        for prop in props:
            setattr(tt, prop, getattr(template, prop))
        return tt

    def __unicode__(self):
        return u"{} for {}".format(self.name, self.event)

class Entitlement(models.Model):
    punter = models.ForeignKey(Punter, related_name='entitlements')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    remaining_uses = models.PositiveIntegerField(null=True, blank=True)

    entitled_to = models.ManyToManyField(BaseTicketInfo, related_name='entitlements')

    def valid(self, at_time=None):
        at_time = at_time or now()

        if self.remaining_uses is not None and self.remaining_uses <= 0:
            # all tickets used
            return False

        if self.start_date is not None and self.start_date > at_time:
            # not yet valid
            return False

        if self.end_date is not None and self.end_date < at_time:
            # passed end of validity
            return False

        return True
    valid.boolean = True

    def __unicode__(self):
        return u"{} entitled to {} ({})".format(
            self.punter, self.entitled_to, 'valid' if self.valid() else 'invalid'
        )

class Ticket(models.Model):
    STATUS = Choices('live', 'void', 'refunded')

    ticket_type = models.ForeignKey(TicketType, related_name='tickets', null=False)

    punter = models.ForeignKey(Punter, related_name='tickets', null=True)
    entitlement = models.ForeignKey(Entitlement, related_name='entitlements', null=True)

    timestamp = models.DateTimeField(null=False, blank=False)
    status = StatusField(db_index=True)

    def __unicode__(self):
        return u"{} ticket for {}".format(self.status, self.ticket_type)
