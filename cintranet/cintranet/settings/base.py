# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
import sys
sys.path.append(os.path.dirname(os.path.dirname(BASE_DIR)))

# useful snippet
from django.core.exceptions import ImproperlyConfigured
def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the {} environment variable".format(var_name)
        raise ImproperlyConfigured(error_msg)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'at94$edi+y2c5-p2p+rl&kex@krdi4$4_-5_8blv2%^3qsydiw'
SSO_SHARED_SECRET_KEY = '5b0G50yVw53zLYiG8o04OjQqWglm7E1U'
DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = [
    'staff.wide.icucinema.co.uk',
    'staff.icucinema.co.uk',
    'staff.wide.imperialcinema.co.uk',
    'staff.imperialcinema.co.uk',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'floppy_gumby_forms',
    'floppyforms',
    'djangular',
    'rest_framework',
    'rest_framework.authtoken',

    'sitewide',
    'auth',
    'ticketing',
    'cott',

    'south',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sitewide.middleware.LoginRequiredMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
)

ROOT_URLCONF = 'cintranet.urls'

WSGI_APPLICATION = 'cintranet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cintranet',
        'USER': get_env_variable('CINTRANET_DB_USER'),
        'PASSWORD': get_env_variable('CINTRANET_DB_PASSWORD'),
        'HOST': get_env_variable('CINTRANET_DB_HOST')
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media')

import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType
AUTH_LDAP_SERVER_URI = "ldap://su-cinema-ernie.su.ic.ac.uk"
AUTH_LDAP_START_TLS = True
AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=people,dc=icucinema,dc=co,dc=uk"
AUTH_LDAP_REQUIRE_GROUP = "cn=staff,ou=groups,dc=icucinema,dc=co,dc=uk"
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "roomNumber"   
}
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_superuser": "cn=staff,ou=groups,dc=icucinema,dc=co,dc=uk",
    "is_staff": "cn=staff,ou=groups,dc=icucinema,dc=co,dc=uk",
    "is_active": "cn=staff,ou=groups,dc=icucinema,dc=co,dc=uk"
}
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=icucinema,dc=co,dc=uk",
    ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
)
AUTH_LDAP_GROUP_TYPE = PosixGroupType()
AUTH_LDAP_FIND_GROUP_PERMS = True


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'PAGINATE_BY': 20,
    'PAGINATE_BY_PARAM': 'per_page',
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
}

LOGIN_URL = '/user/login/'
LOGIN_EXEMPT_URLS = (
    '^$',
    '^ticketing/api/',
    '^remoteheader/$',
    '^ticketing/events/ical/$',
)

### ticketing settings
TICKETING_MEMBERSHIP_ENTITLEMENT = 1
TICKETING_SEASON_ENTITLEMENT = 2
TICKETING_STANDARD_EVENT_TYPE = 1
TICKETING_DOUBLEBILL_EVENT_TYPE = 2
TMDB_API_KEY = "91555fc0d844a9ff2177850a87a88294"

INTERNAL_IPS = [
	'127.0.0.1',
	'::1',
	'155.198.243.16', # su-cinema04
	'155.198.243.25', # su-cinema
]

DEBUG_TOOLBAR_PATCH_SETTINGS = False
