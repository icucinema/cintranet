from .base import *

DEBUG = TEMPLATE_DEBUG = False

INSTALLED_APPS += [
    'raven.contrib.django.raven_compat',
]

RAVEN_CONFIG = {
    'dsn': 'https://19725784cb1843b3b2ee739cd59e9f6e:e28045310d044139a5c30e4c72ad28d6@app.getsentry.com/19013',
}

SECRET_KEY = get_env_variable("CINTRANET_SECRET_KEY")
SSO_SHARED_SECRET_KEY = get_env_variable("CINTRANET_SSO_KEY")
#MAILMAN_ADMIN_PASSWORD = get_env_variable("CINTRANET_MAILMAN_PASSWORD")
MAILMAN_ADMIN_PASSWORD = "perthrop"

STATIC_ROOT = "/srv/www/vhosts/staff/httpdocs/static"
MEDIA_ROOT = "/srv/www/vhosts/staff/httpdocs/media"
AUTH_LDAP_SERVER_URI = "ldap://localhost"
AUTH_LDAP_START_TLS = False

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SSO_COOKIE_SETTINGS = {
	'domain': '.icucinema.co.uk',
	'httponly': True,
	'secure': True
}

SESSION_COOKIE_DOMAIN='.icucinema.co.uk'
