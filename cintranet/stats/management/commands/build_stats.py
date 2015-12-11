import csv
import collections
import datetime
import codecs
import traceback

import requests

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils.timezone import utc

from icunion.eactivities import EActivities
from icusync.models import AuthenticationCredential
import stats.models as models
from cintranet.utils import IRCCatPinger

THIS_YEAR = 2015
THIS_YEARS_MEMBERSHIP_ID = 13396
LAST_YEARS_MEMBERSHIP_ID = 8066
EHACK_URL = 'http://ehacktivities.lukegb.com:5000'

class Command(BaseCommand):
    args = 'eactivities_session_key'
    help = 'Builds the statistics data using the specified eActivities session'
    can_import_settings = True

    def handle(self, *args, **kwargs):
        from django.conf import settings

        if len(args) < 1:
            session = AuthenticationCredential.objects.get(auth_slug="eactivities_session").auth_data
        elif len(args) == 0:
            session = args[0]
        elif len(args) > 1:
            raise CommandError(u"Too many arguments!")

        self.eac = EActivities(session)

        self.club_id = getattr(settings, 'EACTIVITIES_CLUB_ID', 411)

        self.irc_pinger = IRCCatPinger('localhost', 22222)

        with transaction.atomic():
            try:
                self.ehack = requests.session()
                print session
                self.ehack.headers['Authorization'] = 'Token ' + self.ehack.post('{}/session'.format(EHACK_URL), data={'session': session}).json()['token']

                self.update_membership_blob()
                self.update_products_blobs()
                self.update_money_blob()
            except Exception as ex:
                traceback.print_exc()
                self.irc_pinger.say('#botspam', 'SOMETHING WENT WRONG WHILE PARSING EACTIVITIES: {}: {} ({})'.format(type(ex), ex, ex.args))

    def update_membership_blob(self):
        self.update_membership_data('membership_last_year', LAST_YEARS_MEMBERSHIP_ID, '14-15')
        self.update_membership_data('membership_this_year', THIS_YEARS_MEMBERSHIP_ID, '15-16')

    def update_membership_data(self, key, membership_id, year):
        self.stdout.write("Processing {} for {} from {}".format(membership_id, key, year))

        members_joined_on = collections.OrderedDict()

        pr = self.eac.fetch_purchase_report(self.club_id, membership_id, 'product', year)
        for line in pr:
            d = datetime.datetime.strptime(line['Date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            members_joined_on[d] = members_joined_on.get(d, 0) + 1

        obj, created = models.StatsData.objects.get_or_create(key=key, defaults={'value': members_joined_on})
        if not created:
            obj.value = members_joined_on
            obj.save()

    def update_products_blobs(self):
        products = self.fetch_active_products()

        interesting_products = [x for x in products if not x['inactive']]

        obj, created = models.StatsData.objects.get_or_create(key='active_products', defaults={'value': interesting_products})
        if not created:
            obj.value = interesting_products
            obj.save()

        for product in interesting_products:
            self.update_product_data(product['id'])

    def fetch_active_products(self):
        self.stdout.write("Updating products list...")
        resp = self.ehack.get("{}/clubs/{}/{}/products".format(EHACK_URL, self.club_id, THIS_YEAR))
        if resp.status_code == 404:
            return []
        self.stdout.write("Products list: %r" % (resp.json(),))
        return resp.json()

    def update_product_data(self, product_id):
        self.stdout.write("Updating product data for {}...".format(product_id))
        purchasers = self.ehack.get("{}/clubs/{}/{}/products/{}/purchasers".format(EHACK_URL, self.club_id, THIS_YEAR, product_id)).json()

        import json; self.stdout.write(json.dumps(purchasers))

        out_data = {}
        
        for purchaser in purchasers:
            out_data[purchaser['date']] = out_data.get(purchaser['date'], 0) + 1

        out_data = collections.OrderedDict(sorted(out_data.iteritems(), key=lambda x: x[0]))

        obj, created = models.StatsData.objects.get_or_create(key='products_{}'.format(product_id), defaults={'value': out_data})
        if not created:
            obj.value = out_data
            obj.save()

    def update_money_blob(self):
        self.stdout.write("Updating SGI data")
        money = self.ehack.get("{}/clubs/{}/{}/finances".format(EHACK_URL, self.club_id, THIS_YEAR)).json()
        
        obj, created = models.StatsData.objects.get_or_create(key='finances', defaults={'value': money})
        if not created:
            obj.value = money
            obj.save()
