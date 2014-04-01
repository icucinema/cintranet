from .production import *

DEBUG = TEMPLATE_DEBUG = True

INSTALLED_APPS += ['debug_toolbar',]

MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware',]

SESSION_COOKIE_DOMAIN = None
AUTH_LDAP_SERVER_URI = "ldap://su-cinema-ernie.su.ic.ac.uk"
AUTH_LDAP_START_TLS = False
STATIC_ROOT = "static"
MEDIA_ROOT = "media"

SSO_COOKIE_SETTINGS = {}

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda req: DEBUG and not req.is_ajax()
}
