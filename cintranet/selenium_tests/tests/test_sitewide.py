from django.contrib.auth.models import User
from icusync.models import Product
from django.core.urlresolvers import reverse

from ..test import SeleniumTestCase
from ..webdriver import CustomWebDriver

class MainAppTestCase(SeleniumTestCase):

    def setUp(self):
        from django.conf import settings
        if settings.DEBUG == False:
            settings.DEBUG = True

        User.objects.create_superuser(username='admin',
                                      password='pw',
                                      email='root@icucinema.co.uk')
        Product.objects.create(name='Cinema Membership 14-15',
                               currently_available=True,
                               sold=100)

        self.wd = CustomWebDriver()

    def tearDown(self):
        self.wd.quit()

    def test_homepage(self):
        # George goes to the staff homepage
        self.open('/')

        # George sees that the title is "Imperial Cinema Staff Area"
        self.assertIn('Imperial Cinema Staff Area', self.wd.title)

        # He notices that there is a header, with several options and a logo:
        navbar = self.wd.find_element_by_css_selector('.navcontain .navbar')
        header_logo = navbar.find_element_by_css_selector('h1.logo a')
        self.assertIn('IMPERIAL CINEMA', header_logo.text)
        header_links = navbar.find_elements_by_css_selector('li > a')
        for link_text in ['Staff', 'Web', 'eActivities', 'Wiki', 'Trac', 'Cloud']:
            self.assertTrue(
                any(link.text == link_text for link in header_links)
            )

        # He notices that he is invited to log in
        self.assertTrue(
            any(link.text == 'Log in' for link in header_links)
        )

        # He closes the webpage

    def test_members_count(self):
        # Jonny opens the homepage
        self.open('/')

        self.wd.wait_for_css('.btn.primary.medium')

        # He notices Cinema has 100 members
        members_btn = self.wd.find_css('.row .twelve.columns .btn.primary.medium button')
        self.assertIn('Members:', members_btn.text)
        self.assertIn('100', members_btn.text)

        # Someone in the background buys membership 300 times due to a bug in imperialcollegeunion.org
        membership = Product.objects.get(name='Cinema Membership 14-15')
        membership.sold += 300
        membership.save()

        # Jonny gets impatient and refreshes the page
        self.open('/')

        # He notices Cinema now has 400 members
        members_btn = self.wd.find_css('.row .twelve.columns .btn.primary.medium button')
        self.assertIn('Members:', members_btn.text)
        self.assertIn('400', members_btn.text)

    def test_homepage_login(self):
        # James goes to the staff homepage
        self.open('/')

        # He sees that he isn't logged in and clicks the link
        login_link = self.wd.find_css('.index-header .twelve.columns p small a')
        self.assertEquals(login_link.text, 'log in')
        login_link.click()

        self.wd.wait_for_css('#id_username')

        # Now he's presented with a login page
        self.assertIn('Log in', self.wd.title)

        # So he types his username into the username box...
        self.wd.find_css('#id_username').send_keys('admin')
        # his password into the password box
        self.wd.find_css('#id_password').send_keys('pw')
        # and clicks the login button
        self.wd.find_css('button[type=submit]').click()

        # Now he's back on the homepage
        self.wd.wait_for_css('.index-header')
        # and he is welcomed to the site
        self.assertIn('Welcome back,', self.wd.find_css('body .twelve .success.alert').text)

    def test_login_fail(self):
        # Jack opens the login page
        self.open(reverse('auth:login'))

        self.wd.wait_for_css('#id_username')
        self.assertIn('Log in', self.wd.title)

        # He manages to fat finger everything on the page
        self.wd.find_css('#id_username').send_keys('jadfbnkaerh')
        self.wd.find_css('#id_password').send_keys('passward')
        self.wd.find_css('button[type=submit]').click()

        self.wd.wait_for_css('.errorlist')
        errors = self.wd.find_css('.errorlist').find_elements_by_css_selector('li')

        # He is presented by one error
        self.assertEqual(len(errors), 1)
        # which simply tells him he typed something wrong.
        self.assertEqual(errors[0].text, 'Your username or password were incorrect.')
