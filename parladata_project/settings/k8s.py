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
    MEDIA_ROOT=os.getenv('DJANGO_MEDIA_ROOT', '/media/')
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

# static files for development
#STATIC_URL = '/static/'
STATIC_ROOT = env['STATIC_ROOT']

# static files for production
STATIC_URL = env['STATIC_URL']

# Mail settings
# TODO
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'host.si'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'

# TODO what is this
ADMINS = [('admin', 'admin@mail.com')]
DATA_ADMINS = [('data admin', 'dataadmin@mail.com')]
PARSER_ADMINS = [('parser admin', 'parseradmin@mail.com')]

# TODO we should probably delete this
# while refactoring `sendMailForEditVotes`
PARLALIZE_API_KEY = 'parlalize_api_key'

# TODO we should probably delete this
# while refactoring `lockSetter`
SETTER_KEY = 'setter_api_key'

# TODO this should probably disappear
DASHBOARD_URL = 'http://localhost:8881'

# TODO this would be awesome if we could
# set it from admin -> some kind of settings
# module thing or just use the classification
# of the organization to determine it
# National Assembly id in database
DZ_ID = 1

# TODO what is this
# this looks redundant and overridden in
# parladata/utils.py
PS = 'pg'

# TODO what is this
# this looks redundant and overridden in
# parladata/utils.py
PS_NP = ['pg', 'unaligned MP']

# TODO what is this
PS_NP_D = ['pg', 'unaligned MP', 'club']

# TODO what is this
WBS = ['committee',
       'comission',
       'investigative comission']

# TODO what is this
FRIENDSHIP_GROUP = ['friendship group']

# TODO what is this
DELEGATION = ['delegation']

# TODO what is this
COUNCIL = ['council']

# TODO what is this
#['ministrstvo', 'vlada']
MINISTRY_GOV = ['ministry', 'gov']

# TODO what is this
GOV_STAFF = ['gov_service', 'gov_office']

# TODO tip seje, da se ne bo to kar
# iz imena parsalo on the fly (nujna, izredna ...)
