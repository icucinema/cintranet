from django.conf import settings
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait


#determine the WebDriver module. default to Firefox
try:
    web_driver_module = settings.SELENIUM_WEBDRIVER
except AttributeError:
    from selenium.webdriver.firefox import webdriver as web_driver_module


class CustomWebDriver(web_driver_module.WebDriver):
    """Our own WebDriver with some helpers added"""

    def find_css(self, css_selector, el=None):
        """Shortcut to find elements by CSS. Returns either a list or singleton"""
        el = el or self
        elems = el.find_elements_by_css_selector(css_selector)
        found = len(elems)
        if found == 1:
            return elems[0]
        elif not elems:
            return []
        return elems

    def find_visible_css(self, css_selector, el=None):
        el = el or self
        candidates = el.find_elements_by_css_selector(css_selector)
        elems = [e for e in candidates if e.is_displayed()]
        if len(elems) == 1:
            return elems[0]
        elif not elems:
            return []
        return elems

    def wait_for_css(self, css_selector, timeout=7):
        """ Shortcut for WebDriverWait"""
        try:
            return WebDriverWait(self, timeout).until(lambda driver : driver.find_visible_css(css_selector))
        except:
            raise

    def wait_for_css_gone(self, css_selector, timeout=7):
        """ Shortcut for WebDriverWait"""
        try:
            return WebDriverWait(self, timeout).until(lambda driver : not driver.find_visible_css(css_selector))
        except:
            raise

    def has_alert(self, content, type_, exact=True):
        elems = self.find_elements_by_css_selector('.alert.' + type_)
        for elem in elems:
            if exact and elem.text == content:
                return True
            elif not exact and content in elem.text:
                return True
        raise NoSuchElementException(css_selector)
        
    def clear_and_send_keys(self, el, data):
        el.clear()
        el.send_keys(data)