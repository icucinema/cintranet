import requests
from bs4 import BeautifulSoup

DEBUG = True

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

    def _ajax_handler(self, **kwargs):
        new_kwargs = self._munge_params(kwargs)

        if DEBUG:
            print "Fetching", self._ajax_handler_url, "with", new_kwargs

        resp = self.r.post(self._ajax_handler_url, data=new_kwargs)

        if DEBUG:
            print "Got status code", resp.status_code, "with text", resp.text

        return resp

    @property
    def _data_handler_url(self):
        return "https://{}/common/data_handler.php".format(self.base_domain)

    def _data_handler(self, **kwargs):
        new_kwargs = self._munge_params(kwargs)

        if DEBUG:
            print "Fetching", self._data_handler_url, "with", new_kwargs

        resp = self.r.get(self._data_handler_url, params=new_kwargs)

        if DEBUG:
            print "Got status code", resp.status_code

        return resp

    def fetch_members_report(self, club_id):
        # preselect the correct club
        self.r.get(self._members_report_start_url(club_id))

        # setup the session...
        self._ajax_handler(ajax='setup', navigate='3')

        # click on the members tab...
        r = self._ajax_handler(ajax='activatetabs', navigate='395')
        # todo: parse this to create a "proper" list of life/associate members
        
        # and download the report
        r = self._data_handler(id_='1700', type_='csv', name='Members_Report')
        return r

    def fetch_purchase_report(self, club_id, product_id, product_type='product'):
        # preselect the correct club
        self.r.get(self._purchase_report_start_url(club_id))

        # open the page...
        self._ajax_handler(ajax='setup', navigate='847')

        # click on 'purchases summary'
        self._ajax_handler(ajax='activatetabs', navigate='1725')

        # and download the report
        if product_type == 'product':
            r = self._data_handler(id_='1774', type_='csv', name='Purchase_Report', searchstr='ProductGroup', searchvalue=str(product_id))
        elif product_type == 'sku':
            r = self._data_handler(id_='1766', type_='csv', name='Purchase_Report', searchstr='ProductID', searchvalue=str(product_id))
        return r

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print "{} <eActivities session cookie>".format(sys.argv[0])
        sys.exit(1)

    e = EActivities(sys.argv[1])
    print e.fetch_members_report(411).text
    print e.fetch_purchase_report(411, 5219).text
