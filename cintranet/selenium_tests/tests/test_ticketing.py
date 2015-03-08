from django.contrib.auth.models import User
from icusync.models import Product
from ticketing import models
from django.core.urlresolvers import reverse
import random

from ..test import SeleniumTestCase
from ..webdriver import CustomWebDriver

class LoggedInTestCase(SeleniumTestCase):
    def setUp(self):
        User.objects.create_superuser(username='admin',
                                      password='pw',
                                      first_name='James',
                                      email='root@icucinema.co.uk')
        self.log_in('admin', 'pw')

    def assertButtonsAreGreen(self, buttons):
        for button in buttons:
            self.assertHasClass(button, 'secondary')

    def assertButtonsAreGrey(self, buttons):
        for button in buttons:
            self.assertHasClass(button, 'default')

class NotLoggedInTestCase(SeleniumTestCase):
    def test_requires_login(self):
        self.open(reverse('root'))
        self.assertIn(reverse('auth:login'), self.wd.current_url)

class PuntersTestCase(LoggedInTestCase):
    def setUp(self):
        punter_jane_doe = models.Punter.objects.create(
            punter_type=models.Punter.STATUS.full,
            name='Jane Doe',
            cid='00516767',
            login='jd1311',
            email='jane.doe11@imperial.ac.uk',
            comment='some comment here'
        )
        ent_test = models.Entitlement.objects.create(
            name='Test Entitlement',
        )
        entdet_test_jane_doe = models.EntitlementDetail.objects.create(
            punter=punter_jane_doe,
            entitlement=ent_test,
        )
        super(PuntersTestCase, self).setUp()

    def createPunter(self, n):
        year = str(random.randint(9, 15)).zfill(2)
        models.Punter.objects.create(
            punter_type=models.Punter.STATUS.full,
            name='Punter J{}'.format(n),
            cid=str(random.randint(0, 99999999)).zfill(8),
            login='pj{}{}'.format(str(n).zfill(2), year),
            email='punter.j{}{}@imperial.ac.uk'.format(n, year),
            comment='some comment here'
        )


    def test_can_list(self):
        self.open(reverse('root') + '#/punters')
        self.wd.wait_for_css('table.striped')

        punter_table = self.wd.find_visible_css('table.striped')
        punter_rows = punter_table.find_elements_by_css_selector('tbody > tr')
        self.assertEqual(len(punter_rows), 1)
        punter_row = punter_rows[0]
        self.assertEqual(punter_row.find_elements_by_css_selector('td')[0].text, 'Jane Doe')
        self.assertEqual(punter_row.find_elements_by_css_selector('td')[1].text, '00516767')

    def get_next_buttons(self):
        btns = self.wd.find_visible_css('.medium.btn.icon-right.icon-arrow-right')
        self.assertEqual(len(btns), 2)
        return btns

    def get_prev_buttons(self):
        btns = self.wd.find_visible_css('.medium.btn.icon-left.icon-arrow-left')
        self.assertEqual(len(btns), 2)
        return btns

    def click_first_button_and_wait(self, btns):
        btn = btns[0]
        btn.find_element_by_css_selector('a').click()
        self.wd.wait_for_css('table.striped')
        self.wd.wait_for_css('table.striped > tbody > tr')

    def click_next(self):
        self.click_first_button_and_wait(self.get_next_buttons())

    def click_prev(self):
        self.click_first_button_and_wait(self.get_prev_buttons())

    def test_can_page(self):
        for n in range(20):
            self.createPunter(n)
        self.open(reverse('root') + '#/punters')
        self.wd.wait_for_css('table.striped')
        
        nextBtns = self.get_next_buttons()
        prevBtns = self.get_prev_buttons()
        self.assertButtonsAreGreen(nextBtns)
        self.assertButtonsAreGrey(prevBtns)

        self.click_next()
        
        nextBtns = self.get_next_buttons()
        prevBtns = self.get_prev_buttons()
        self.assertButtonsAreGreen(nextBtns)
        self.assertButtonsAreGreen(prevBtns)

        self.click_next()

        nextBtns = self.get_next_buttons()
        prevBtns = self.get_prev_buttons()
        self.assertButtonsAreGrey(nextBtns)
        self.assertButtonsAreGreen(prevBtns)
        
        self.click_prev()

        nextBtns = self.get_next_buttons()
        prevBtns = self.get_prev_buttons()
        self.assertButtonsAreGreen(nextBtns)
        self.assertButtonsAreGreen(prevBtns)

        self.click_prev()
        
        nextBtns = self.get_next_buttons()
        prevBtns = self.get_prev_buttons()
        self.assertButtonsAreGreen(nextBtns)
        self.assertButtonsAreGrey(prevBtns)

    def test_can_drill_down(self):
        self.open(reverse('root') + '#/punters')
        self.wd.wait_for_css('table.striped')

        punter_table = self.wd.find_visible_css('table.striped')
        punter_rows = punter_table.find_elements_by_css_selector('tbody > tr')
        punter_row = punter_rows[0]
        punter_row.find_element_by_css_selector('td a').click()

        self.wd.wait_for_css('section.tabs')

        self.assertAnyElement('h2', lambda el: el.text == 'Jane Doe')

        data = {
            'Union Membership Type': 'Full member',
            'CID': '00516767',
            'Username': 'jd1311',
            'Email': 'jane.doe11@imperial.ac.uk',
            'Comment': 'some comment here',
        }
        for k, v in data.iteritems():
            self.assertAnyElement('dt', lambda el: el.text == k and self.assertAnyElement('dd', lambda el: el.text == v, el.parent))

    def test_can_edit(self):
        self.open(reverse('root') + '#/punters')
        self.wd.wait_for_css('table.striped')

        punter_table = self.wd.find_visible_css('table.striped')
        punter_rows = punter_table.find_elements_by_css_selector('tbody > tr')
        punter_row = punter_rows[0]
        punter_row.find_element_by_css_selector('td a').click()

        self.wd.wait_for_css('section.tabs')
        self.wd.find_visible_css('.medium.primary.btn a').click()

        self.wd.find_visible_css('[ng-model="edit_data.punter_type"]').send_keys('A')
        self.wd.clear_and_send_keys(self.wd.find_visible_css('[ng-model="edit_data.name"]'), 'Janet Doe')
        self.wd.clear_and_send_keys(self.wd.find_visible_css('[ng-model="edit_data.cid"]'), '00666747')
        self.wd.clear_and_send_keys(self.wd.find_visible_css('[ng-model="edit_data.login"]'), 'jpd1311')
        self.wd.clear_and_send_keys(self.wd.find_visible_css('[ng-model="edit_data.email"]'), 'janet.doe11@imperial.ac.uk')
        self.wd.clear_and_send_keys(self.wd.find_visible_css('[ng-model="edit_data.comment"]'), 'Was previously Jane Doe (incorrectly)')
        self.wd.find_visible_css('.medium.success.btn a').click()

        self.wd.wait_for_css_gone('.medium.success.btn')

        data = {
            'Union Membership Type': 'Associate/life member',
            'CID': '00666747',
            'Username': 'jpd1311',
            'Email': 'janet.doe11@imperial.ac.uk',
            'Comment': 'Was previously Jane Doe (incorrectly)',
        }
        self.assertAnyElement('h2', lambda el: el.text == 'Janet Doe')
        for k, v in data.iteritems():
            self.assertAnyElement('dt', lambda el: el.text == k and self.assertAnyElement('dd', lambda el: el.text == v, el.parent))

        # test reloading, too
        self.open(reverse('root') + '#/punters')
        self.wd.wait_for_css('table.striped')

        punter_table = self.wd.find_visible_css('table.striped')
        punter_rows = punter_table.find_elements_by_css_selector('tbody > tr')
        punter_row = punter_rows[0]
        punter_row.find_element_by_css_selector('td a').click()

        self.wd.wait_for_css('section.tabs')

        self.assertAnyElement('h2', lambda el: el.text == 'Janet Doe')
        for k, v in data.iteritems():
            self.assertAnyElement('dt', lambda el: el.text == k and self.assertAnyElement('dd', lambda el: el.text == v, el.parent))

    def test_can_view_entitlements(self):
        self.open(reverse('root') + '#/punters')
        self.wd.wait_for_css('table.striped')

        punter_table = self.wd.find_visible_css('table.striped')
        punter_rows = punter_table.find_elements_by_css_selector('tbody > tr')
        punter_row = punter_rows[0]
        punter_row.find_element_by_css_selector('td a').click()

        self.wd.wait_for_css('section.tabs')
        self.wd.find_visible_css('section.tabs').find_element_by_partial_link_text('Entitlements').click()

        self.assertEqual(self.wd.find_visible_css('section.tabs').find_element_by_partial_link_text('Entitlements').text, 'Entitlements (1)')
        tab_content = self.wd.find_visible_css('.tab-content.active')
        tab_list_els = tab_content.find_elements_by_css_selector('ul.bulleted-list > li')
        self.assertEqual(len(tab_list_els), 1)
        tab_list_el = tab_list_els[0]
        self.assertAllElements('h5', lambda el: 'Test Entitlement' in el.text and self.assertHasClass(el, 'valid'), tab_list_el)

    def test_can_edit_entitlements(self):
        self.open(reverse('root') + '#/punters')
        self.wd.wait_for_css('table.striped')

        punter_table = self.wd.find_visible_css('table.striped')
        punter_rows = punter_table.find_elements_by_css_selector('tbody > tr')
        punter_row = punter_rows[0]
        punter_row.find_element_by_css_selector('td a').click()

        self.wd.wait_for_css('section.tabs')
        self.wd.find_visible_css('section.tabs').find_element_by_partial_link_text('Entitlements').click()

        self.assertEqual(self.wd.find_visible_css('section.tabs').find_element_by_partial_link_text('Entitlements').text, 'Entitlements (1)')
        tab_content = self.wd.find_visible_css('.tab-content.active')
        tab_list_els = tab_content.find_elements_by_css_selector('ul.bulleted-list > li')
        self.assertEqual(len(tab_list_els), 1)
        tab_list_el = tab_list_els[0]

        edit_button = self.wd.find_visible_css('.primary.medium.btn > a', tab_list_el)
        self.assertEqual(edit_button.text, 'Edit')
        edit_button.click()

        button_input = self.wd.find_visible_css('input[type="number"]', tab_list_el)
        button_input.clear()
        button_input.send_keys('0')

        save_button = self.wd.find_visible_css('.success.btn > a', tab_list_el)
        self.assertEqual(save_button.text, 'Save')
        save_button.click()

        self.open(reverse('root') + '#/punters')
        self.wd.wait_for_css('table.striped')

        punter_table = self.wd.find_visible_css('table.striped')
        punter_rows = punter_table.find_elements_by_css_selector('tbody > tr')
        punter_row = punter_rows[0]
        punter_row.find_element_by_css_selector('td a').click()

        self.wd.wait_for_css('section.tabs')
        self.wd.find_visible_css('section.tabs').find_element_by_partial_link_text('Entitlements').click()

        self.assertEqual(self.wd.find_visible_css('section.tabs').find_element_by_partial_link_text('Entitlements').text, 'Entitlements (1)')
        tab_content = self.wd.find_visible_css('.tab-content.active')
        tab_list_els = tab_content.find_elements_by_css_selector('ul.bulleted-list > li')
        self.assertEqual(len(tab_list_els), 1)
        tab_list_el = tab_list_els[0]
        self.assertAllElements('h5', lambda el: 'Test Entitlement' in el.text and self.assertHasClass(el, 'invalid'), tab_list_el)

        edit_button = self.wd.find_visible_css('.primary.medium.btn > a', tab_list_el)
        self.assertEqual(edit_button.text, 'Edit')
        edit_button.click()

        button_input = self.wd.find_visible_css('input[type="number"]', tab_list_el)
        button_input.clear()
        button_input.send_keys('1')

        save_button = self.wd.find_visible_css('.success.btn > a', tab_list_el)
        self.assertEqual(save_button.text, 'Save')
        save_button.click()

        self.open(reverse('root') + '#/punters')
        self.wd.wait_for_css('table.striped')

        punter_table = self.wd.find_visible_css('table.striped')
        punter_rows = punter_table.find_elements_by_css_selector('tbody > tr')
        punter_row = punter_rows[0]
        punter_row.find_element_by_css_selector('td a').click()

        self.wd.wait_for_css('section.tabs')
        self.wd.find_visible_css('section.tabs').find_element_by_partial_link_text('Entitlements').click()

        self.assertEqual(self.wd.find_visible_css('section.tabs').find_element_by_partial_link_text('Entitlements').text, 'Entitlements (1)')
        tab_content = self.wd.find_visible_css('.tab-content.active')
        tab_list_els = tab_content.find_elements_by_css_selector('ul.bulleted-list > li')
        self.assertEqual(len(tab_list_els), 1)
        tab_list_el = tab_list_els[0]
        self.assertAllElements('h5', lambda el: 'Test Entitlement' in el.text and self.assertHasClass(el, 'valid'), tab_list_el)