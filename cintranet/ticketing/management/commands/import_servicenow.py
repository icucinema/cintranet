import csv
import datetime
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.timezone import utc, now

from ticketing import models

def today():
    return now().strftime('%Y-%m-%d %H:%M:%S')

class Command(BaseCommand):
    args = 'path_to_sys_users'
    help = 'Imports the specified sys_user.csv into the database'
    can_import_settings = True

    def handle(self, *args, **kwargs):
        if len(args) < 1:
            raise CommandError(u"Must pass the path to sys_user.csv")
        elif len(args) > 1:
            raise CommandError(u"Too many arguments!")

        members_report_path, = args
        with open(members_report_path, 'rb') as csvfile:
            csvr = csv.DictReader(csvfile)

            count_total = 0
            count_errored = 0
            count_already_exist = 0
            count_created = 0

            with transaction.atomic():
                for member in csvr:
                    try:
                        _, created = self.handle_member(member)
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

            self.stdout.write("")
            self.stdout.write("RESULTS")
            self.stdout.write("-------")
            self.stdout.write("")
            self.stdout.write("CATEGORY\tMEMBER COUNT")
            self.stdout.write("Created:\t{}".format(count_created))
            self.stdout.write("Existing:\t{}".format(count_already_exist))
            self.stdout.write("Errored:\t{}".format(count_errored))
            self.stdout.write("Total:\t\t{}".format(count_total))

    def handle_member(self, csv_row):
        # massage the data set
        cid = csv_row['employee_number'].decode('utf-8')
        name = csv_row['name'].decode('utf-8')
        note = u"Imported from Service-Now on {}".format(
            today()
        )
        email = csv_row['email']
        username = csv_row['user_name']
        punter_type = 'full'

        filter_on = {'cid': cid}
        self.stdout.write(u'Handling {} (CID: {}, username: {})'.format(name, cid, username))

        obj, created = models.Punter.objects.get_or_create(
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

        return obj, created
