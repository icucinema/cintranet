from .base import *

DEBUG = TEMPLATE_DEBUG = True

INSTALLED_APPS += ['debug_toolbar',]

MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware',]

AUTH_LDAP_SERVER_URI = "ldap://ldap.icucinema.co.uk"
AUTH_LDAP_START_TLS = True
STATIC_ROOT = "static"
MEDIA_ROOT = "media"

SSO_COOKIE_SETTINGS = {}

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda req: DEBUG and not req.is_ajax()
}
