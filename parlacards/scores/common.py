from datetime import datetime, timedelta
from string import punctuation
import re

from django.utils.module_loading import import_string
from django.conf import settings


def get_dates_between(datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    number_of_days = (datetime_to - datetime_from).days

    return [(datetime_from + timedelta(days=i)) for i in range(number_of_days)]

def get_fortnights_between(datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    number_of_fortnights = (datetime_to - datetime_from).days % 14

    return [(datetime_from + timedelta(days=(i * 14))) for i in range(number_of_fortnights)]

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', punctuation))

def tokenize(text):
    return [s for s in re.split(r'\s', text) if s != '']

def get_lemmatize_method(name, language_code=None):
    '''
    name: name of lemmatizer method for import
    '''
    if not language_code:
        language_code = getattr(
            settings, 'LEMMATIZER_LANGUAGE_CODE',
        )

    mathod_path_string = f'parlacards.lemmatizers.{language_code}.lemmatizer.{name}'
    method = import_string(mathod_path_string)
    return method

def get_mandate_of_playing_field(playing_field):
    playing_field_membership = playing_field.organization_memberships.first()
    if playing_field_membership:
        mandate = playing_field_membership.mandate
        if mandate:
            return mandate
        else:
            raise Exception('Playing field membership has not mandate')
    raise Exception('Playing field has not membership')

def get_time_range_from_mandate(mandate, timestamp):
    if mandate.beginning:
        from_timestamp = mandate.beginning
    else:
        from_timestamp = datetime.min

    if mandate.ending and mandate.ending < timestamp:
        to_timestamp = mandate.ending
    else:
        to_timestamp = timestamp

    return from_timestamp, to_timestamp
