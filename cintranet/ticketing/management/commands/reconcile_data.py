import csv
import datetime
import codecs
import traceback
import requests

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count
from django.utils.timezone import utc

import ticketing.models

class Command(BaseCommand):
    args = ''
    help = 'Reconciles data in database (e.g. multiple Punters with same CID/missing information)'
    can_import_settings = True

    def handle(self, *args, **kwargs):
        self.handle_duplicate_cids()

    def handle_duplicate_cids(self):
        dupes = ticketing.models.Punter.objects.all() \
            .order_by('cid').values('cid').annotate(Count('cid')) \
            .filter(cid__count__gt=1).exclude(cid__exact='') \
            .values_list('cid', flat=True)

        self.stdout.write("-- CID DEDUPLICATION: {} DUPLICATES --".format(len(dupes)))

        for cid in dupes:
            pn = list(ticketing.models.Punter.objects.filter(cid=cid))
            self.stdout.write("Deduplicating CID: {} - {} dupes".format(cid, len(pn)))
            self.deduplicate(pn)

        self.stdout.write("-- CID DEDUPLICATION COMPLETE: {} DUPLICATES --".format(len(dupes)))

    def dedup_score(self, punter):
        score = 0

        if punter.name != '':
            score += 50
        if punter.email != '':
            score += 25
        if punter.swipecard != '':
            score += 15
        if punter.login != '':
            score += 15
        if punter.comment != '':
            score += 20 + len(punter.comment)
        score += punter.tickets.count()
        score += (10 * punter.entitlements.count())

        return score

    def copy_data(self, main_punter, punter):
        fields = ['name', 'email', 'swipecard', 'login']
        for field in fields:
            main_p_data = getattr(main_punter, field)
            p_data = getattr(punter, field)
            if main_p_data == '' and p_data != '':
                setattr(main_punter, field, p_data)

        if punter.description != '':
            main_punter.description += '\r\n\r\nMERGED DATA:\r\n' + punter.description

    def deduplicate(self, punters):
        main_punter = None
        main_punter_score = 0
        for punter in punters:
            punter_score = self.dedup_score(punter)
            if main_punter is None or main_punter_score < punter_score:
                main_punter, main_punter_score = punter, punter_score

        for punter in punters:
            if punter == main_punter:
                continue

            # reassign entitlement details
            punter.entitlement_details.update(punter=main_punter)
            # reassign tickets
            punter.tickets.update(punter=main_punter)

            self.copy_data(main_punter, punter)

            punter.delete()

        main_punter.save()
        return main_punter
