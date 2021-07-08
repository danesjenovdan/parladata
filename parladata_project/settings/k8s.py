# -*- coding: utf-8 -*-
from .defaults import *

# generate your secret key with
# python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
env = dict(
    SECRET_KEY=os.getenv('DJANGO_SECRET_KEY', 'r^&^$8c*g$6db1s!s7uk9c!v%*ps)_0)h$!f3m7$%(o4b+5qwk'),
    DEBUG=os.getenv('DJANGO_DEBUG', True),
    DATABASE_HOST=os.getenv('DJANGO_DATABASE_HOST', 'localhost'),
    DATABASE_PORT=os.getenv('DJANGO_DATABASE_PORT', '5432'),
    DATABASE_NAME=os.getenv('DJANGO_DATABASE_NAME', 'parladata'),
    DATABASE_USER=os.getenv('DJANGO_DATABASE_USER', 'postgres'),
    DATABASE_PASSWORD=os.getenv('DJANGO_DATABASE_PASSWORD', 'postgres'),
    STATIC_ROOT=os.getenv('DJANGO_STATIC_ROOT', os.path.join(BASE_DIR, '../static')),
    STATIC_URL=os.getenv('DJANGO_STATIC_URL_BASE', '/static/'),
    MEDIA_ROOT=os.getenv('DJANGO_MEDIA_ROOT', '/media/'),
    MEDIA_URL=os.getenv('DJANGO_MEDIA_URL_BASE', '/media/'),
    SOLR_URL=os.getenv('PARLAMETER_SOLR_URL', ''),
)



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env['SECRET_KEY']
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env['DEBUG']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': env['DATABASE_HOST'],
        'PORT': env['DATABASE_PORT'],
        'NAME': env['DATABASE_NAME'],
        'USER': env['DATABASE_USER'],
        'PASSWORD': env['DATABASE_PASSWORD'],
    }
}

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': 'cache:11211', # TODO get cache address from env
#         'TIMEOUT': None,
#     }
# }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': None,
    }
}

# static files for development
#STATIC_URL = '/static/'
STATIC_ROOT = env['STATIC_ROOT']

# static files for production
STATIC_URL = env['STATIC_URL']

MEDIA_ROOT = env['MEDIA_ROOT']
MEDIA_URL = env['MEDIA_URL']

SOLR_URL = env['SOLR_URL']


# Mail settings

EMAIL_BACKEND = os.getenv('PARLAMETER_EMAIL_BACKEND', 'django.core.mail.backends.filebased.EmailBackend')
EMAIL_FILE_PATH = os.getenv('PARLAMETER_EMAIL_FILE_PATH', '/tmp/emails')
EMAIL_USE_TLS = bool(os.getenv('PARLAMETER_EMAIL_USE_TLS', True))
EMAIL_HOST = os.getenv('PARLAMETER_EMAIL_HOST', 'dummy')
EMAIL_PORT = int(os.getenv('PARLAMETER_EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('PARLAMETER_SMTP_USER', 'dummy')
EMAIL_HOST_PASSWORD = os.getenv('PARLAMETER_SMTP_PASSWORD', 'dummy')
FROM_EMAIL = os.getenv('PARLAMETER_FROM_EMAIL', 'test@test.si')
