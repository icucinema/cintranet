# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import re
from decimal import Decimal
from io import BytesIO
from delorean import Delorean

import requests
from bs4 import BeautifulSoup

from . import encoding_utils

DEBUG = False

TOTAL_NET_SALE_RE = re.compile(r"^Provisional Total Net Sale \([^)]+\)$")
PRICE_INC_VAT_RE = re.compile(r"^Price inc. VAT/Unit \([^)]+\)$")

class EActivitiesEvent(object):
    def __init__(self):
        self.centre = 172
        self.event_type = 3
        self.name = ''
        self.description = ''
        self.postcode = ''
        self.start_date = datetime.now()
        self.end_date = datetime.now() + timedelta(seconds=60*60)
        self.banner_image = None

    def __unicode__(self):
        return u'EActivitiesEvent: "{}" ({}) start:{} end:{}'.format(self.name, self.description, self.start_date, self.end_date)
    def __str__(self):
        return unicode(self).encode('utf-8')

    @property
    def start_date_in_london(self):
        return Delorean(self.start_date).shift('Europe/London').datetime

    @property
    def end_date_in_london(self):
        return Delorean(self.end_date).shift('Europe/London').datetime

class MemberListMunger(object):
    def __init__(self, itera, associate_pairs):
        self.itera = itera
        self.associate_pairs = associate_pairs

    def __iter__(self):
        return self

    def munge(self, record):
        rr = [record['First Name'], record['Surname']]
        record['Status'] = 'full'
        naps = list(self.associate_pairs)
        for rb in self.associate_pairs:
            if rb[0] == rr[0] and rb[1] == rr[1]:
                record['Status'] = 'life'
                naps.remove(rb)
                break
        if len(self.associate_pairs) != len(naps):
            self.associate_pairs = naps
        return record

    def next(self, *args, **kwargs):
        return self.munge(self.itera.next(*args, **kwargs))

class EActivities(object):
    def __init__(self, session_cookie, base_domain='eactivities.union.ic.ac.uk'):
        self.r = requests.session()
        self.base_domain = base_domain
        sess_cookie = {
            "version":0,
            "name":'ICU_eActivities',
            "value":session_cookie,
            "port":None,
            "domain":base_domain,
            "path":'/',
            "secure":False,
            "expires":None,
            "discard":True,
            "comment":None,
            "comment_url":None,
            "rest":{},
            "rfc2109":False
        }
        self.r.cookies.set(**sess_cookie)

    @property
    def _ajax_handler_url(self):
        return "https://{}/common/ajax_handler.php".format(self.base_domain)

    @property
    def _file_handler_url(self):
        return "https://{}/common/file_handler.php".format(self.base_domain)

    def _members_report_start_url(self, club_id):
        return "https://{}/admin/csp/details/{}".format(self.base_domain, club_id)

    def _purchase_report_start_url(self, club_id):
        return "https://{}/finance/income/shop/{}".format(self.base_domain, club_id)

    def _munge_params(self, kwargs):
        new_kwargs = {}
        for k, v in kwargs.items():
            if k.endswith('__'):
                k = k[:-2] + "[]"
            elif k.endswith('_'):
                k = k[:-1]
            new_kwargs[k] = v
        return new_kwargs

    def _ajax_handler(self, stream=False, **kwargs):
        new_kwargs = self._munge_params(kwargs)

        if DEBUG:
            print "Fetching", self._ajax_handler_url, "with", new_kwargs

        resp = self.r.post(self._ajax_handler_url, data=new_kwargs, stream=stream)
        resp.encoding = 'utf8'

        if DEBUG:
            print "Got status code", resp.status_code, "with text", resp.text

        return resp

    @property
    def _data_handler_url(self):
        return "https://{}/common/data_handler.php".format(self.base_domain)

    def _data_handler(self, stream=False, **kwargs):
        new_kwargs = self._munge_params(kwargs)

        if DEBUG:
            print "Fetching", self._data_handler_url, "with", new_kwargs

        resp = self.r.get(self._data_handler_url, params=new_kwargs, stream=stream)
        resp.encoding = 'utf8'

        if DEBUG:
            print "Got status code", resp.status_code

        return resp

    def _request_page(self, url, stream=False):
        if DEBUG:
            print "Fetching", url, "(as GET)"

        if not url.startswith('http'):
            url = 'https://{}{}'.format(self.base_domain, url)

        resp = self.r.get(url, stream=stream)
        resp.encoding = 'utf8'

        if DEBUG:
            print "Got status code", resp.status_code

        return resp

    def upload_file(self, navigate, filename, file_data, file_mime):
        file_data = {'files[]': (filename, file_data, file_mime)}
        if DEBUG:
            print "Uploading file..."
        resp = self.r.post(self._file_handler_url, files=file_data, data={'navigate': navigate})
        resp.encoding = 'utf8'
        if DEBUG:
            print "Got status code", resp.status_code, resp.text
        resp.raise_for_status()
        return u'returnvalue">0' in resp.text

    def create_event(self, event):
        self._request_page("https://{}/admin/csp/whatson".format(self.base_domain)).raise_for_status()
        self._ajax_handler(ajax='setup', navigate='2780')
        kws = {
            'data[2794]': event.centre,
            'data[2782]': event.event_type,
            'data[2783]': event.name,
            'data[2784]': event.description,
            'data[2788]': event.location,
            'data[4123]': event.postcode,
            'data[2786]': event.start_date_in_london.strftime('%Y-%m-%d %H:%M:%S'),
            'data[2787]': event.end_date_in_london.strftime('%Y-%m-%d %H:%M:%S'),
        }
        self._ajax_handler(ajax='insertsql', navigate='2781', **kws)
        self._ajax_handler(ajax='update', navigate='2781')
        if event.banner_image:
            self.upload_file('2791', 'hi-ajc.jpg', event.banner_image, 'image/jpeg')
            self._ajax_handler(ajax='update', navigate='1211')
        self._ajax_handler(ajax='submit', navigate='2781', Submitted='1', ajax_id='0', ajax_type='2')

    def read_associate_members_list(self, mlxml):
        s = BeautifulSoup(mlxml)
        people = s.find_all(id=re.compile('^1083-'), alias='Name')
        associates = []
        for p in people:
            p = p.text
            if p.endswith(' - Life / Associate'):
                z = p.find(' (')
                if z == -1:
                    z = p.find(' -')
                pers = p[0:z].strip().split(', ')[::-1]
                associates.append(pers)
        return associates

    def fetch_members_report(self, club_id):
        # preselect the correct club
        self.r.get(self._members_report_start_url(club_id))

        # setup the session...
        self._ajax_handler(ajax='setup', navigate='3')

        # click on the members tab...
        r = self._ajax_handler(ajax='activatetabs', navigate='395')
        associates = self.read_associate_members_list(r.text)
        
        # and download the report
        r = self._data_handler(id_='1700', type_='csv', name='Members_Report', stream=True)

        return MemberListMunger(self.parse_report_csv(r.raw, flo=True), associates)

    def _open_purchases_summary(self, club_id):
        # preselect the correct club
        self.r.get(self._purchase_report_start_url(club_id))

        # open the page...
        self._ajax_handler(ajax='setup', navigate='847')

        # click on 'purchases summary'
        return self._ajax_handler(ajax='activatetabs', navigate='1725')

    def fetch_available_products(self, club_id):
        ps = self._open_purchases_summary(club_id)

        bs = BeautifulSoup(ps.content)
        bs_prs = bs.find("enclosure", label="Purchase Reports").find_all("infotable")

        prs = []
        for bs_pr in bs_prs:
            skus = []
            title = bs_pr.attrs['title']
            title = title[:title.rfind('(')-1]
            pr = {
                'name': title,
                'eactivities_id': int(bs_pr.attrs['linkobj'].rpartition('/')[-1]),
                'skus': skus,
                'purchased_count': 0,
                'total': Decimal(0),
            }
            bs_skus = bs_pr.find_all("infotablerow")
            for bs_sku in bs_skus:
                print bs_sku
                tns = bs_sku.find('infotablecell', alias=TOTAL_NET_SALE_RE).text.replace(',', '')
                if tns == u'\xa0': tns = '0'
                sku = {
                    'name': bs_sku.find('infotablecell', alias="Product SKU Name").text,
                    'eactivities_id': int(bs_sku.find('infotablecell', alias="Download").attrs['linkobj'].rpartition('/')[-1]),
                    'purchased_count': max(0, int(bs_sku.find('infotablecell', alias="Number Purchased").text)),
                    'total': max(Decimal(0), Decimal(tns)),
                    'per_item': Decimal(bs_sku.find('infotablecell', alias=PRICE_INC_VAT_RE).text.replace(',', '')),
                }
                pr['purchased_count'] += sku['purchased_count']
                pr['total'] += sku['total']
                skus.append(sku)
            prs.append(pr)
        return prs

    def fetch_purchase_report(self, club_id, product_id, product_type='product', year=None):
        if year is not None:
            # fml
            ps = self._open_purchases_summary(club_id)
            bs = BeautifulSoup(ps.content)
            year_tab = bs.find("tabenclosure", label=year)
            if year_tab.attrs.get('active', 'false') != 'true':
                self.r.post('https://{}{}'.format(self.base_domain, '/common/ajax_handler.php'), data={'ajax': 'activatetabs', 'navigate': year_tab.attrs['id']})

        # and download the report
        if product_type == 'product':
            r = self._request_page('/finance/income/shop/group/csv/{}'.format(product_id))
        elif product_type == 'sku':
            r = self._request_page('/finance/income/shop/product/csv/{}'.format(product_id))

        return self.parse_report_csv(r.content, flo=False)

    def parse_report_csv(self, report_data, flo=False):
        if not flo:  # file-like object
            c = BytesIO(report_data)
        else:
            c = report_data
        
        return encoding_utils.EActivitiesDictCsvReader(c)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print "{} <eActivities session cookie>".format(sys.argv[0])
        sys.exit(1)

    DEBUG = True
    e = EActivities(sys.argv[1])
    #print list(e.fetch_members_report(411))
    #print list(e.fetch_purchase_report(411, 21725, 'sku'))
    from pprint import pprint
    pprint(e.fetch_available_products(411))
