from .base import *

DEBUG = TEMPLATE_DEBUG = False

SECRET_KEY = get_env_variable("CINTRANET_SECRET_KEY")
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'cintranet',
    'USER': get_env_variable('CINTRANET_DB_USER'),
    'PASSWORD': get_env_variable('CINTRANET_DB_PASSWORD'),
    'HOST': get_env_variable('CINTRANET_DB_HOST')
}