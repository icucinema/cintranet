# - encoding: utf-8 -

import csv
import datetime
import codecs
import traceback

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils.timezone import utc

from icusync import models
from icunion import collate, eactivities
import ticketing.models
from cintranet.utils import IRCCatPinger

class Command(BaseCommand):
    args = 'start ID'
    help = 'Creates whats on events, starting from the given Showing ID'
    can_import_settings = True

    def handle(self, *args, **kwargs):
        from django.conf import settings

        session = models.AuthenticationCredential.objects.get(auth_slug="eactivities_session").auth_data
        if len(args) != 1:
            raise CommandError(u"Takes one argument!")
        showing_id = int(args[0])

        self.club_id = getattr(settings, 'EACTIVITIES_CLUB_ID', 411)

        self.irc_pinger = IRCCatPinger('localhost', 22222)

        try:
            self.eac = eactivities.EActivities(session)
    
            self.sync_showings(showing_id)
        except Exception as ex:
            traceback.print_exc()
            self.irc_pinger.say('##icucinema.botspam', 'SOMETHING WENT WRONG WHILE PARSING EACTIVITIES: {}: {} ({})'.format(type(ex), ex, ex.args))

    def fetch_banner(self, showing):
        return requests.get(showing.week.film.hero_image_url, stream=True).raw

    def make_eactivities_event(self, showing):
        ev = eactivities.EActivitiesEvent()
        ev.name = u'{} @ Imperial Cinema'.format(showing.week.film.name)
        pricing_info = ticketing.models.TicketType.objects.filter(event__showings=showing, is_public=True).order_by('sale_price')
        pricing_text = u' / '.join([u'£{} {}'.format(x.sale_price, x.name) for x in pricing_info])
        ev.description = u'<p>{}</p><p>Tickets: {}</p><p>For more information about this film, please see <a href="http://www.imperialcinema.co.uk">our website</a>.</p>'.format(showing.week.film.description, pricing_text)
        ev.postcode = u'SW7 2BB'
        ev.location = u'Imperial Cinema, 2nd Floor Union Building, Beit Quad'
        ev.start_date = showing.start_time
        film_len = showing.week.film.length + 14
        ev.end_date = showing.start_time + datetime.timedelta(seconds=60 * film_len)
        ev.banner_image = self.fetch_banner(showing)
        return ev

    def sync_showings(self, showing_id):
        showings = ticketing.models.Showing.objects.filter(id__gte=showing_id, is_public=True, start_time__gte=datetime.datetime.now()).order_by('id').select_related('week_film')
        for showing in showings:
            ev = self.make_eactivities_event(showing)
            self.eac.create_event(ev)
