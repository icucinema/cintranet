from .base import *

DEBUG = TEMPLATE_DEBUG = False

INSTALLED_APPS += ['selenium_tests']

AUTH_LDAP_SERVER_URI = "ldap://ldap.icucinema.co.uk"
AUTH_LDAP_START_TLS = True
STATIC_ROOT = "static"
MEDIA_ROOT = "media"


SSO_COOKIE_SETTINGS = {}

class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
MIGRATION_MODULES = DisableMigrations()

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)