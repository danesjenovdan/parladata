from datetime import datetime, timedelta
from string import punctuation

from tagger.lemmatiser import Lemmatiser

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


# TODO lemmatization only works for slovenian
# initialize the lemmatizer class only once
lemmatiser = Lemmatiser()
def lemmatize(token):
    return lemmatiser.lemmatise_token(token)[0][1]

def lemmatize_many(tokens):
    return [x[1] for x in lemmatiser.tag_lemmatise_sent(tokens)]
