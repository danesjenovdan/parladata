import os
import raven

from defaults import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'exkqi8xb2vnn4a*fyh@1y)z7*amz0!9p15ce9acqotf@y*wjn&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'parladata',
        'USER': 'parladaddy',
        'PASSWORD': 'razvrat',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = 'http://djstatic.knedl.si/parladata/static/'
STATIC_ROOT = '/home/muki/djstatic/parladata/static/'

RAVEN_CONFIG = {
    'dsn': '' #'http://338491150ce2417fb770eb4afa77102f:b9b2bf8011b14643b4bd8eabd3e367f4@sentry.ilol.si/40',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
#    'release': raven.fetch_git_sha(os.path.dirname(__file__)),
}

# Mail settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'posta.owca.info'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'muki'
EMAIL_HOST_PASSWORD = 'Iamanonsmoker'

ADMINS = [('Tomaz Kunst', 'cofek0@gmail.com')]

DATA_ADMINS = [('Nika Mahnic', 'nmahnich@gmail.com'),
               ('Ziga Vrtacic', 'ziga.vrtacic@gmail.com')]

PARSER_ADMINS = [('Primoz Klemenske', 'klemensek@gmail.com')]

PARLALIZE_API_KEY = 'vednoboljsi112358'
SETTER_KEY = 'vednoboljsi112358'

DASHBOARD_URL = 'https://dashboard.knedl.si'


