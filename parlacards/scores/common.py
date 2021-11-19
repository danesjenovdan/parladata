from datetime import datetime, timedelta
from string import punctuation

from django.utils.module_loading import import_string
from django.conf import settings


def get_dates_between(datetime_from=datetime.now(), datetime_to=datetime.now()):
    number_of_days = (datetime_to - datetime_from).days

    return [(datetime_from + timedelta(days=i)) for i in range(number_of_days)]

def get_fortnights_between(datetime_from=datetime.now(), datetime_to=datetime.now()):
    number_of_fortnights = (datetime_to - datetime_from).days % 14

    return [(datetime_from + timedelta(days=(i * 14))) for i in range(number_of_fortnights)]

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', punctuation))

def tokenize(text):
    return [s for s in text.split(' ') if s != '']

def get_lemmatize_method(name):
    '''
    name: name of lemmatizer method for import
    '''
    language_code = getattr(
        settings, 'LEMMATIZER_LANGUAGE_CODE',
    )
    mathod_path_string = f'parlacards.lemmatizers.{language_code}.lemmatizer.{name}'
    method = import_string(mathod_path_string)
    return method
