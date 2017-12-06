# -*- coding: utf-8 -*-
import os
import raven
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = (
    'taggit',
    'djgeojson',
    'leaflet',
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'parladata',
    'parlasearch',
    'django_extensions',
    'raven.contrib.django.raven_compat',
    'corsheaders',
    'rest_framework',
    'taggit_serializer',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'parladata_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "parladata/data")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'parladata_project.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'sl-si'

TIME_ZONE = 'Europe/Ljubljana'

USE_I18N = True

USE_L10N = True

USE_TZ = False

API_DATE_FORMAT = '%d.%m.%Y'

MANDATE_START_TIME = datetime(day=31, month=7, year=2014)

# CORS config
CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = { 
    'DEFAULT_PERMISSION_CLASSES': [ 
        'rest_framework.permissions.IsAdminUser', 
    ],
    #'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10, 
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
}

VOTE_CLASSIFICATIONS = { 
    '1': ['dnevni red', 'širitev dnevnega reda', 'umik točke dnevnega reda'], 
    '2': ['glasovanje o zakonu v celoti'], 
    '3': ['amandma'], 
    '4': ['interpelacija'], 
    '5': ['evidenčni sklep'], 
    '6': ['predlog sklepa'], 
    '7': ['zakon o ratifikaciji'], 
    '8': ['sklep o imenovanju', 
          'predlog za imenovanje', 
          'izvolitev', 
          'soglasje k imenovanju', 
          'predlog kandidata', 
          'predlog kandidatke', 
          'sklep o izvolitvi', 
          'predlog za izvolitev'], 
    '9': ['predlog za razpis'], 
    '10': ['priporočilo'], 
    '11': ['poročilo'], 
    '12': ['proceduralni predlog'], 
    '13': ['odlok o načrtu ravnanja s stvarnim premoženjem'],
}
