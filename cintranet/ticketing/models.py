import itertools
import re
import string
import random
from decimal import Decimal

from django.db import models, transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now
from django.conf import settings

from model_utils.managers import InheritanceManager
from model_utils.fields import StatusField
from model_utils import Choices
from tmdbsimple import TMDB
import requests

ACCEPTABLE_CHARACTERS_RE = re.compile(r'[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\' \-_]+')
Q = models.Q
F = models.F
tmdb = TMDB(settings.TMDB_API_KEY)
_tmdb_conf = None
tmdb_url_re = re.compile(r'^https?://[a-z\.]+/movie/(?P<tmdb_id>\d+)-.*$')


def tmdb_config():
    global _tmdb_conf
    if _tmdb_conf is None:
        _tmdb_conf = tmdb.Configuration()
        _tmdb_conf.info()
    return _tmdb_conf


def tmdb_construct_poster(img_bit, size='original'):
    if img_bit is None:
        return None
    c = tmdb_config()
    return c.images['base_url'] + size + img_bit


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

    def available_tickets(self, events, at_time=None, on_door=True, online=False):
        return TicketType.objects.filter(
            Q(event__in=events) &
            (
                Q(
                    general_availability=True,
                    sell_on_the_door=on_door,
                    sell_online=online,
                ) | Q(
                    Q(
                        EntitlementDetail.valid_q_obj("entitlements__entitlement_details__", at_time=at_time),
                        entitlements__entitlement_details__punter=self,
                    ) | Q(
                        EntitlementDetail.valid_q_obj("template__entitlements__entitlement_details__", at_time=at_time),
                        template__entitlements__entitlement_details__punter=self,
                    ),
                    general_availability=False,
                )
            )
        )

    @classmethod
    def create_from_eactivities_csv(cls, csv_row, entitlements, note, write_to=lambda x: None):
        # massage the data set
        cid = csv_row['CID/Card Number']
        name = u"{} {}".format(csv_row['First Name'], csv_row['Last Name'])
        email = csv_row['Email']
        username = csv_row['Login']
        punter_type = csv_row.get('Status', 'full' if cid != '' else 'associate')

        filter_on = {}
        if cid != '' and not cid.startswith('AM-'):
            filter_on = {'cid': cid}
            write_to(u'Handling {} (CID: {}, username: {})'.format(name, cid, username))
        else:
            filter_on = {'name': name}
            write_to(u'Handling {} (associate/life member)'.format(name))

        obj, created = cls.objects.get_or_create(
            defaults={
                'cid': cid,
                'name': name,
                'comment': note,
                'email': email,
                'login': username,
                'punter_type': punter_type
            },
            **filter_on
        )

        entitlements_created = 0
        # check if entitlements already exist
        for ent_id, ent_kwargs in entitlements.iteritems():
            eobj, c = EntitlementDetail.objects.get_or_create(
                punter=obj,
                entitlement_id=ent_id,
                defaults=ent_kwargs
            )
            if c:
                entitlements_created += 1
            if c and not created:
                obj.comment += '\n' + note
                
        obj.save() # in case comment has changed

        return obj, created, entitlements_created

    class Meta:
        ordering = ['name']


class Film(models.Model):
    tmdb_id = models.PositiveIntegerField(null=True, blank=True)
    imdb_id = models.CharField(max_length=20, null=False, blank=True, default="")

    name = models.CharField(max_length=256, default="", null=False, blank=False)
    sorting_name = models.CharField(max_length=256, null=False, blank=False)
    description = models.TextField(default="", null=False, blank=True)
    certificate = models.CharField(max_length=12, default="", null=False, blank=False)

    poster_url = models.URLField(blank=True, null=False, default="")

    def __unicode__(self):
        return self.name

    def update_sorting_name(self):
        removing_prefixes = ['the ', ]
        n = self.name.lower()
        for remove_prefix in removing_prefixes:
            if n.startswith(remove_prefix):
                n = n[len(remove_prefix):]
        self.sorting_name = n

    def save(self, *args, **kwargs):
        self.update_sorting_name()
        super(Film, self).save(*args, **kwargs)

    @classmethod
    def from_tmdb(cls, tmdb_id):
        if 'themoviedb.org' in str(tmdb_id):
            # it looks like a URL...
            tmdb_match = tmdb_url_re.search(tmdb_id)
            if not tmdb_match:
                return None
            tmdb_id = tmdb_match.groupdict().get('tmdb_id', None)
        self = cls(tmdb_id=int(tmdb_id))
        self.update_tmdb()
        return self

    @classmethod
    def search_tmdb(cls, query):
        search = tmdb.Search()
        search.movie({'query': query})
        return [cls.from_tmdb(r['id']) for r in search.results]

    def update_tmdb(self):
        movie = tmdb.Movies(self.tmdb_id)
        movie.info({'append_to_response': 'releases'})
        self.name = movie.title
        self.description = movie.overview
        self.imdb_id = movie.imdb_id
        self.poster_url = tmdb_construct_poster(movie.poster_path)
        for country in movie.releases['countries']:
            if country['iso_3166_1'] == 'GB':
                self.certificate = country['certification']

    def update_imdb(self):
        resp = requests.get("http://www.imdb.com/title/{}/parentalguide".format(self.imdb_id))
        if resp.status_code != 200:
            return
        txt = resp.text
        n = txt.find('<h5>Certification:</h5>')
        txt = txt[n:]
        n = txt.find('</div>')
        txt = txt[:n]
        n = txt.find('">UK:') + len('">UK:')
        p = txt.find('</a>', n)
        self.certificate = txt[n:p]

    def update_remote(self):
        if self.tmdb_id is not None and self.tmdb_id != 0:
            self.update_tmdb()
        if self.imdb_id != "":
            self.update_imdb()
        self.save()

    class Meta:
        ordering = ['sorting_name']


class Showing(models.Model):
    film = models.ForeignKey(Film, related_name='showings', null=False, blank=False)
    start_time = models.DateTimeField(null=False, blank=False)
    primary_event = models.OneToOneField('Event', related_name='primary_showing', null=True, blank=True)

    def __unicode__(self):
        return u"{} ({})".format(self.film.name, self.start_time)

    def create_event(self):
        ev = Event(
            name=self.film.name,
            start_time=self.start_time
        )
        ev.save()
        self.primary_event = ev

    def tickets(self):
        return Ticket.objects.filter(ticket_type__event__showings=self)

    def total_take(self):
        return self.tickets().aggregate(models.Sum('ticket_type__sale_price'))

    def total_bor(self):
        return self.tickets().aggregate(models.Sum('ticket_type__box_office_return_price'))

    def save(self, *args, **kwargs):
        doap = False
        try:
            if self.primary_event is None:
                raise Event.DoesNotExist
        except Event.DoesNotExist:
            self.create_event()
            doap = True

        ret = super(Showing, self).save(*args, **kwargs)

        ev = self.primary_event
        if doap:
            ev.event_types = [EventType.objects.get(pk=settings.TICKETING_STANDARD_EVENT_TYPE)]
            ev.showings.add(self)
            ev.create_ticket_types_by_event_types()

        ev.name = self.film.name
        ev.start_time = self.start_time
        ev.save()

        return ret

    class Meta:
        ordering = ['start_time']


class BoxOfficeReturn(models.Model):
    raw_data = models.TextField(null=False, blank=False)
    pdf_file = models.FileField(upload_to='box_office_returns', null=False, blank=False)
    film = models.ForeignKey(Film, related_name='box_office_returns')
    start_time = models.DateField(null=False, blank=False)

    @property
    def fake_filename(self):
        import bor_generator
        show_week = self.start_time
        show_week_str = show_week.strftime('%Y-%m-%d')

        cleaned_film_name = ACCEPTABLE_CHARACTERS_RE.sub('', self.film.name)

        return "{} {}.pdf".format(show_week_str, cleaned_film_name)


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
            
    @property
    def tickets(self):
        return Ticket.objects.filter(ticket_type__event=self)

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
        help_text="""This is the inc-VAT (gross) price reported on the BOR for *each* film"""
    )
    name = models.CharField(max_length=128, null=False, blank=False)
    print_template_extension = models.CharField(max_length=64, null=False, blank=True, default='')

    objects = InheritanceManager()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['sale_price']


class TicketTemplate(BaseTicketInfo):
    event_type = models.ManyToManyField(EventType, related_name='ticket_templates')


class TicketType(BaseTicketInfo):
    event = models.ForeignKey(Event)

    template = models.ForeignKey(TicketTemplate, blank=True, null=True)

    @classmethod
    def from_template(cls, template, event):
        props = (
            'online_description',
            'sell_online',
            'sell_on_the_door',
            'general_availability',
            'sale_price',
            'name',
            'print_template_extension',
            'box_office_return_price'
        )
        tt = cls(
            template=template,
            event=event
        )
        for prop in props:
            setattr(tt, prop, getattr(template, prop))
        return tt

    def sale_price_for_punter(self, punter=None, at_time=None):
        if punter is None:
            return self.sale_price

        if at_time is None:
            # infer from event time
            at_time = self.event.start_time

        # check if punter has any EntitlementDetails allowing this ticket at a discount
        qs_filter = Q(entitlement__entitled_to=self) & EntitlementDetail.valid_q_obj(at_time=at_time)
        if self.template is not None:
            qs_filter = qs_filter | Q(entitlement__entitled_to=self.template)
        qs_filter = qs_filter & Q(punter=punter, discount__gt=0)
        qs = EntitlementDetail.objects.filter(qs_filter).order_by('-discount')

        if qs:
            # they do have a discounted rate EntitlementDetail!
            return (1 - (Decimal(qs[0].discount) / 100)) * self.sale_price
        return self.sale_price

    def __unicode__(self):
        return u"{} for {}".format(self.name, self.event)


class EntitlementDetail(models.Model):
    punter = models.ForeignKey(Punter, related_name='entitlement_details')
    entitlement = models.ForeignKey('Entitlement', related_name='entitlement_details')
    created_on = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    remaining_uses = models.PositiveIntegerField(null=True, blank=True)
    discount = models.PositiveSmallIntegerField(null=False, blank=False, default=0)

    def valid(self, at_time=None):
        if self.remaining_uses is not None and self.remaining_uses <= 0:
            # all used up
            return False

        # delegate it to the base entitlement validity checker
        return self.entitlement.valid(at_time)

    valid.boolean = True

    @staticmethod
    def valid_q_obj(prefix="", at_time=None):
        remaining_uses_q_kw = Q(**{
            prefix + "remaining_uses__isnull": True
        }) | Q(**{
            prefix + "remaining_uses__gt": 0
        })

        return remaining_uses_q_kw & Entitlement.valid_q_obj(prefix + "entitlement__", at_time)

    def name(self):
        return self.entitlement.name

    class Meta:
        unique_together = (('punter', 'entitlement'),)


class Entitlement(models.Model):
    punters = models.ManyToManyField(Punter, related_name='entitlements', through=EntitlementDetail)
    name = models.CharField(max_length=255, null=False, blank=False, db_index=True, unique=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    entitled_to = models.ManyToManyField(BaseTicketInfo, related_name='entitlements')

    def valid(self, at_time=None):
        at_time = at_time or now()

        if self.start_date is not None and self.start_date > at_time:
            # not yet valid
            return False

        if self.end_date is not None and self.end_date < at_time:
            # passed end of validity
            return False

        return True

    valid.boolean = True

    @property
    def entitled_to_subclasses(self):
        return self.entitled_to.all().select_subclasses()

    @staticmethod
    def valid_q_obj(prefix="", at_time=None):
        at_time = at_time or now()

        start_date_q_kw = Q(**{
            prefix + "start_date__isnull": True
        }) | Q(**{
            prefix + "start_date__lt": at_time
        })

        end_date_q_kw = Q(**{
            prefix + "end_date__isnull": True
        }) | Q(**{
            prefix + "end_date__gt": at_time
        })

        return start_date_q_kw & end_date_q_kw

    def __unicode__(self):
        return u"{} ({})".format(
            self.name, 'valid' if self.valid() else 'invalid'
        )


class Ticket(models.Model):
    STATUS = Choices('live', 'void', 'refunded')

    ticket_type = models.ForeignKey(TicketType, related_name='tickets', null=False)

    punter = models.ForeignKey(Punter, related_name='tickets', null=True)
    entitlement = models.ForeignKey(Entitlement, related_name='tickets', null=True)

    timestamp = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    status = StatusField(db_index=True)

    def __unicode__(self):
        return u"{} ticket for {}".format(self.status, self.ticket_type)

    @classmethod
    def generate(cls, ticket_type, punter=None):
        self = cls()
        self.ticket_type = ticket_type
        self.punter = punter
        self.entitlement = None
        self.status = 'live'

        entitlement_detail = None

        # if this isn't a generally available ticket
        if not ticket_type.general_availability:
            entitled_to_q = Q(entitlement__entitled_to=ticket_type) | Q(entitlement__entitled_to=ticket_type.template)
            base_ed_qs = EntitlementDetail.objects.filter(punter=punter).filter(entitled_to_q)
            base_ed_qs = base_ed_qs.filter(EntitlementDetail.valid_q_obj())
            free_ed_qs = base_ed_qs.filter(remaining_uses=None)
            paid_ed_qs = base_ed_qs.exclude(remaining_uses=None)

            # we need to look for any EntitlementDetails that link us to the punter that don't expire, first
            if not free_ed_qs:  # we might use the result QS
                # there are no "free" entitlements
                # is there a "paid" entitlement?
                if paid_ed_qs:
                    # yes!
                    entitlement_detail = paid_ed_qs[0]
                else:
                    # basically, there's no way that this person is actually entitled to this ticket
                    # so we're just going to display the end result
                    pass
            else:
                # we found a free entitlement. link it up!
                entitlement_detail = free_ed_qs[0]

        if entitlement_detail is not None:
            self.entitlement = entitlement_detail.entitlement

        # this is the important bit
        with transaction.atomic():
            # we save the ticket itself...
            self.save()

            # and decrement the remaining uses of the entitlement!
            if entitlement_detail is not None and entitlement_detail.remaining_uses is not None:
                entitlement_detail.remaining_uses = F('remaining_uses') - 1
                entitlement_detail.save(update_fields=['remaining_uses'])

        return self

    def ticket_position_in_showing(self):
        ev = self.ticket_type.event
        return Ticket.objects.filter(ticket_type__event=ev, id__lte=self.id).count()

    def printed_id(self):
        allowed_chars = string.digits + string.letters

        ev_name = self.ticket_type.event.name
        random_title_char_pos = None
        while random_title_char_pos is None or ev_name[random_title_char_pos] not in allowed_chars:
            random_title_char_pos = random.randint(0, len(ev_name) - 1)
        random_title_char = ev_name[random_title_char_pos].upper()

        return (
                   "%(ticket_id)d/%(ticket_number)d-%(random_title_char_pos)d%(random_title_char)s%(film_day)02d-" +
                   "%(film_word_count)s-" +
                   "%(film_char_count)d"
               ) % {
                   'ticket_id': self.id,
                   'random_title_char': random_title_char,
                   'random_title_char_pos': random_title_char_pos + 1, # humans don't like to 0-index
                   'film_day': self.ticket_type.event.start_time.day,
                   'film_word_count': ''.join([str(len(word)) for word in self.ticket_type.event.name.split()]),
                   'film_char_count': len(self.ticket_type.event.name.split()),
                   'ticket_number': self.ticket_position_in_showing()
               }

    @transaction.atomic
    def refund(self):
        if self.status != 'live':
            raise Exception("Can't refund a non-live ticket!")
        # refunding means we give the money back and we return any entitlements that they lost
        if self.entitlement is not None and self.punter is not None:
            entitlement_detail = self.entitlement.entitlement_details.get(punter=self.punter)
            if entitlement_detail.remaining_uses is not None:
                entitlement_detail.remaining_uses = F('remaining_uses') + 1
                entitlement_detail.save(update_fields=['remaining_uses'])
        self.status = 'refunded'
        self.save()
        return self

    @transaction.atomic
    def void(self):
        if self.status != 'live':
            raise Exception("Can't void a non-live ticket!")
        # voiding means we neither give the money back nor return any entitlements
        self.status = 'void'
        self.save()

    class Meta:
        ordering = ['-id']
