import csv
import datetime
import codecs
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.timezone import utc

from icusync import models
from icunion import collate, eactivities
import ticketing.models
from cintranet.utils import IRCCatPinger

class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **kwargs):
        entitlement_id, filename = args
        with open(filename, 'rb') as f:
            self.update_from_purchase_report(entitlement_id, f.read())

    def update_from_purchase_report(self, sku_e, pr):
        self.stdout.write("Processing entitlements from purchase report".format(sku_e.entitlement.name))

        automatic_entitlements = {
            sku_e.entitlement_id: {
                'remaining_uses': sku_e.uses_remaining
            }
        }

        count_total = 0
        count_errored = 0
        count_already_exist = 0
        count_created = 0

        count_created_ents = 0
        count_already_exist_created_ents = 0
        count_total_ents_created = 0

        with transaction.atomic():
            sku_e.sku.dirty = False
            sku_e.sku.save()
            for member in pr:
                try:
                    _, created, ents_created = ticketing.models.Punter.create_from_eactivities_csv(member, automatic_entitlements, "Purchased {} (order no {})".format(member['Date'], member['Order No']), self.stdout.write, lambda x: self.irc_pinger.say('#icucinema', x))
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

