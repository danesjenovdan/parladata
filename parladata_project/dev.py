import os
import raven

from defaults import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hashhashhashhashashwkopaskfpjoij3rijfdsf2332fdw!!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'parladata',
        'USER': 'parlauser',
        'PASSWORD': 'parlapassword',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

RAVEN_CONFIG = {
    #'dsn': 'http://123sdfsd123:123gdfsg123@sentry.url.si/40',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
#    'release': raven.fetch_git_sha(os.path.dirname(__file__)),
}


# Mail settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'host.si'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'

ADMINS = [('admin', 'admin@mail.com')]

DATA_ADMINS = [('data admin', 'dataadmin@mail.com')]

PARSER_ADMINS = [('parser admin', 'parseradmin@mail.com')]

PARLALIZE_API_KEY = 'parlalize_api_key'
SETTER_KEY = 'setter_api_key'

DASHBOARD_URL = 'http://localhost:8881'

