import csv
import datetime
import codecs
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.timezone import utc

from cott import models
from icunion import collate, eactivities
import ticketing.models

class Command(BaseCommand):
    args = 'eactivities_session_key'
    help = 'Imports all data from eActivities using the specified session key'
    can_import_settings = True

    def handle(self, *args, **kwargs):
        from django.conf import settings

        if len(args) < 1:
            session = models.AuthenticationCredential.objects.get(auth_slug="eactivities_session").auth_data
        elif len(args) == 0:
            session = args[0]
        elif len(args) > 1:
            raise CommandError(u"Too many arguments!")

        self.club_id = getattr(settings, 'EACTIVITIES_CLUB_ID', 411)

        self.eac = eactivities.EActivities(session)

        self.update_available_products()
        self.rescrape_products()

    def update_available_products(self):
        products = collate.get_product_info(self.eac, "https://www.imperialcollegeunion.org/shop/club-society-project-products/cinema-products/", 411)
        with transaction.atomic():
            models.Product.objects.all().update(currently_available=False)
            for product in products.values():
                p, _ = models.Product.objects.get_or_create(
                    eactivities_id=product['eactivities_id'],
                    defaults={
                        'name': product['name'],
                        'sold': product['purchased_count'],
                        'initial': product.get('total_count', None)
                    }
                )
                p.name = product['name']
                p.sold = product['purchased_count']
                if 'total_count' in product.keys():
                    p.initial = product['total_count']
                if 'org_id' in product.keys():
                    p.currently_available = True
                    p.org_id = product['org_id']
                p.save()
    
                for sku in product['skus']:
                    s, _ = models.SKU.objects.get_or_create(
                        product=p,
                        eactivities_id=sku['eactivities_id'],
                        defaults={
                            'name': sku['name'],
                            'sold': sku['purchased_count'],
                            'initial': sku.get('total_count', None)
                        }
                    )
                    s.name = sku['name']
                    s.sold = sku['purchased_count']
                    if 'total_count' in sku.keys():
                        s.initial = sku['total_count']
                    s.dirty = True
                    s.save()

    def rescrape_products(self):
        sku_entitlements = models.SKUEntitlement.objects.filter(
            sku__dirty=True
        )
        purchase_reports = {}
        for sku_e in sku_entitlements:
            # go get the purchase report!
            pr = self.eac.fetch_purchase_report(self.club_id, sku_e.sku.eactivities_id, 'sku')
            self.update_from_purchase_report(sku_e, pr)

    def update_from_purchase_report(self, sku_e, pr):
        self.stdout.write("Processing entitlements from SKU for {}".format(sku_e.entitlement.name))

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
                    _, created, ents_created = ticketing.models.Punter.create_from_eactivities_csv(member, automatic_entitlements, "Purchased {} (order no {})".format(member['Date'], member['Order No']), self.stdout.write)
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

