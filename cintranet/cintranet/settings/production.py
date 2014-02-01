from .base import *

DEBUG = TEMPLATE_DEBUG = False

SECRET_KEY = get_env_variable("CINTRANET_SECRET_KEY")
SSO_SHARED_SECRET_KEY = get_env_variable("CINTRANET_SSO_KEY")

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
