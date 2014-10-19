import csv
import datetime
import codecs
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils.timezone import utc

from icusync import models
from icunion import collate, eactivities
import ticketing.models
from cintranet.utils import IRCCatPinger

from pymailman import mailman

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

        self.irc_pinger = IRCCatPinger('localhost', 22222)

        try:
            self.eac = eactivities.EActivities(session)
    
            self.update_available_products()
            self.rescrape_products()
        except Exception as ex:
            traceback.print_exc()
            self.irc_pinger.say('##icucinema.botspam', 'SOMETHING WENT WRONG WHILE PARSING EACTIVITIES: {}: {} ({})'.format(type(ex), ex, ex.args))

    def mailing_list_subscription(self, controller, punters):
        if not controller.subscribe_to_mailing_list:
            return

        self.stdout.write("Subscribing {} people to our mailing list!\n".format(len(punters)))
        self.irc_pinger.say("#icucinema", "Subscribing {} people to our mailing list.".format(len(punters)))

        def _unbreak_emails(x):
            e = x.email
            if e.endswith('@ic.ac.uk'):
                e = e[:-len('@ic.ac.uk')] + '@imperial.ac.uk'
            return e

        emails = map(_unbreak_emails, punters)

        from django.conf import settings
        mman = mailman.MailmanInterface(settings.MAILMAN_LIST, settings.MAILMAN_ADMIN_PASSWORD, settings.MAILMAN_INSTANCE)
        try:
            ok, fail = mman.add_members(emails, invite_to_list=False, send_welcome_message=True, invitation_text=controller.mailing_list_subscribe_header, notify_list_owner=True)
            self.irc_pinger.say('##icucinema.botspam', 'Subscribed {}, failed {}'.format(len(ok), len(fail)))
            self.stdout.write(str(ok) + "\n")
            self.stdout.write(str(fail) + "\n\n")
        except Exception as ex:
            traceback.print_exc()
            self.irc_pinger.say('##icucinema.botspam', 'SOMETHING WENT WRONG WHILE SUBSCRIBING PEOPLE: {}: {} ({})'.format(type(ex), ex, ex.args))

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
                if p.sold != product['purchased_count']:
                    self.irc_pinger.say('#icucinema', '{} purchase count changed! {} -> {}'.format(p.name, p.sold, product['purchased_count']))
                p.sold = product['purchased_count']
                if 'total_count' in product.keys():
                    p.initial = product['total_count']
                if 'org_id' in product.keys():
                    p.currently_available = True
                    p.org_id = product['org_id']
                p.save()
    
                for sku in product['skus']:
                    try:
                        qs = []
                        if sku.get('eactivities_id') is not None:
                            qs.append(Q(eactivities_id=sku['eactivities_id']))
                        if sku.get('org_id') is not None:
                            qs.append(Q(org_id=sku['org_id']))

                        if len(qs) == 0:
                            q = Q(id=-1)
                        else:
                            q = qs[0]
                            for q_ in qs:
                                q |= q_
                        s = models.SKU.objects.get(q)
                    except models.SKU.DoesNotExist:
                        if sku.get('eactivities_id') is not None:
                            s, _ = models.SKU.objects.get_or_create(
                                product=p,
                                eactivities_id=sku['eactivities_id'],
                                defaults={
                                    'name': sku['name'],
                                    'sold': sku['purchased_count'],
                                    'initial': sku.get('total_count', None)
                                }
                            )
                        elif sku.get('org_id') is not None:
                            s, _ = models.SKU.objects.get_or_create(
                                product=p,
                                org_id=sku['org_id'],
                                defaults={
                                    'name': sku['name'],
                                    'sold': sku['purchased_count'],
                                    'initial': sku.get('total_count', None)
                                }
                            )
                        else:
                            print "Failed to find anything useful on", sku['name'], sku.keys()
                            continue
                    if sku.get('eactivities_id'):
                        s.eactivities_id = sku['eactivities_id']
                    if sku.get('org_id'):
                        s.org_id = sku['org_id']
                    s.name = sku['name']
                    s.sold = sku['purchased_count']
                    if sku.get('total_count'):
                        s.initial = sku['total_count']
                    s.dirty = True
                    s.save()

    def rescrape_products(self):
        sku_entitlements = list(models.SKUEntitlement.objects.filter(
            sku__dirty=True
        ))
        sku_tickettypes = list(models.SKUTicketType.objects.filter(
            sku__dirty=True
        ))
        purchase_reports = {}

        for sku_e in sku_entitlements:
            # go get the purchase report!
            pr = self.eac.fetch_purchase_report(self.club_id, sku_e.sku.eactivities_id, 'sku')
            self.update_from_purchase_report(sku_e, pr, 'entitlement')

        for sku_tt in sku_tickettypes:
            pr = self.eac.fetch_purchase_report(self.club_id, sku_tt.sku.eactivities_id, 'sku')
            self.update_from_purchase_report(sku_tt, pr, 'tickettype')

    def update_from_purchase_report(self, sku_e, pr, what):
        self.stdout.write("Processing {}s from SKU for {}".format(what, str(sku_e)))

        if what == 'entitlement':
            automatic_entitlements = {
                what: {
                    sku_e.entitlement_id: {
                        'remaining_uses': sku_e.uses_remaining
                    }
                }
            }
        elif what == 'tickettype':
            automatic_entitlements = {
                what: {
                    sku_e.ticket_type_id: {}
                }
            }

        count_total = 0
        count_errored = 0
        count_already_exist = 0
        count_created = 0

        count_created_ents = 0
        count_already_exist_created_ents = 0
        count_total_ents_created = 0

        punters = []

        with transaction.atomic():
            sku_e.sku.dirty = False
            sku_e.sku.save()
            for member in pr:
                try:
                    punter, created, ents_created = ticketing.models.Punter.create_from_eactivities_csv(member, automatic_entitlements, "Purchased {} (order no {})".format(member['Date'], member['Order No']), lambda x: self.stdout.write(x.encode('utf-8')), lambda x: self.irc_pinger.say('#icucinema', x))
                    if ents_created > 0:
                        punters.append(punter)
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

            if sku_e.subscribe_to_mailing_list and len(punters) > 0:
                self.mailing_list_subscription(sku_e, punters)

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

