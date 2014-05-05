import csv
import datetime
import codecs
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils.timezone import utc

import ticketing.models
from icunion.encoding_utils import EActivitiesDictCsvReader
from cintranet.utils import IRCCatPinger

class Command(BaseCommand):
    args = '[filename] [entitlement ID]'
    help = 'Imports all data from eActivities using the specified session key'
    can_import_settings = True

    def handle(self, *args, **kwargs):
        from django.conf import settings

        self.irc_pinger = IRCCatPinger('localhost', 22222)

        try:
            self.load_and_update(args[0], args[1])
        except Exception as ex:
            traceback.print_exc()

    def load_and_update(self, csv_filename, entitlement_id):
        with open(csv_filename, 'r') as f:
            assert f.readline() == 'Full Members\n'
            mr = EActivitiesDictCsvReader(f)
            self.update_from_purchase_report(entitlement_id, mr)

    def update_from_purchase_report(self, entitlement_id, mr):
        self.stdout.write("Processing members report for {}".format(entitlement_id))

        automatic_entitlements = {
            'entitlement': {
                entitlement_id: {
                    'remaining_uses': None
                }
            }
        }

        count_total = 0
        count_errored = 0
        count_already_exist = 0
        count_created = 0

        count_created_ents = 0
        count_already_exist_created_ents = 0
        count_total_ents_created = 0

        membership_type = 'full'

        with transaction.atomic():
            for member in mr:
                if member['Date'] == 'Life / Associate':
                    membership_type = 'associate'
                    continue

                try:
                    punter, created, ents_created = ticketing.models.Punter.create_from_eactivities_csv(member, automatic_entitlements, "Loaded from Member's Report {} (order no {})".format(member['Date'], member['Order No']), lambda x: self.stdout.write(x.encode('utf-8')), lambda x: self.irc_pinger.say('#botspam', x), membership_type=membership_type)
                except Exception, ex:
                    count_total += 1
                    count_errored += 1
                    traceback.print_exc(file=self.stderr)
                    continue

                count_total += 1
                if created:
                    count_created += 1
                else:
                    count_already_exist += 1
                if ents_created != 0:
                    count_created_ents += 1
                    count_total_ents_created += ents_created
                if not created and ents_created != 0:
                    count_already_exist_created_ents += 1

            self.stdout.write("")
            self.stdout.write("RESULTS")
            self.stdout.write("-------")
            self.stdout.write("")
            self.stdout.write("CATEGORY\tMEMBER COUNT")
            self.stdout.write("Created:\t{}".format(count_created))
            self.stdout.write("Existing:\t{}".format(count_already_exist))
            self.stdout.write("Errored:\t{}".format(count_errored))
            self.stdout.write("Total:\t\t{}".format(count_total))
            self.stdout.write("")
            self.stdout.write("CATEGORY\t\t\tCOUNT")
            self.stdout.write("Created for <n> members:\t{}".format(count_created_ents))
            self.stdout.write("...where member existed:\t{}".format(count_already_exist_created_ents))
            self.stdout.write("Total created:\t\t\t{}".format(count_total_ents_created))

