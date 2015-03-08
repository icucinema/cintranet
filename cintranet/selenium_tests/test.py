from django.test import TestCase, LiveServerTestCase
from django.core.urlresolvers import reverse

from .webdriver import CustomWebDriver

class SeleniumTestCase(LiveServerTestCase):

    @staticmethod
    def get_webdriver():
        return CustomWebDriver()

    @classmethod
    def setUpClass(cls):
        cls.wd = cls.get_webdriver()
        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.wd.quit()
        super(SeleniumTestCase, cls).tearDownClass()

    def open(self, url):
        self.wd.get("%s%s" % (self.live_server_url, url))

    def log_in(self, username, password):
        self.open(reverse('auth:login'))

        self.wd.wait_for_css('#id_username')

        self.wd.find_css('#id_username').send_keys(username)
        self.wd.find_css('#id_password').send_keys(password)
        self.wd.find_css('button[type=submit]').click()

    def assertAnyElement(self, selector, expr, in_el=None):
        base = in_el or self.wd
        self.assertTrue(any(expr(el) for el in base.find_elements_by_css_selector(selector)), 'all of {} failed expectation'.format(selector))
        return True

    def assertAllElements(self, selector, expr, in_el=None):
        base = in_el or self.wd
        self.assertTrue(all(expr(el) for el in base.find_elements_by_css_selector(selector)), 'one of {} failed expectation'.format(selector))
        return True

    def assertHasClass(self, item, class_):
        item_classes = item.get_attribute('class').split(' ')
        self.assertIn(class_, item_classes)
        return True