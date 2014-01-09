from .base import *

DEBUG = TEMPLATE_DEBUG = False

SECRET_KEY = get_env_variable("CINTRANET_SECRET_KEY")
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'cintranet',
    'USER': get_env_variable('CINTRANET_DB_USER'),
    'PASSWORD': get_env_variable('CINTRANET_DB_PASSWORD'),
    'HOST': get_env_variable('CINTRANET_DB_HOST')
}
