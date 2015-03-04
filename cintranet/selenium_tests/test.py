from django.test import TestCase, LiveServerTestCase

class SeleniumTestCase(LiveServerTestCase):
    def open(self, url):
        self.wd.get("%s%s" % (self.live_server_url, url))
