from datetime import datetime

from parladata.models.speech import Speech

from parlacards.models import PersonNumberOfSpokenWords

from parlacards.scores.common import (
    get_dates_between,
    get_fortnights_between,
)

def calculate_number_of_spoken_words(speeches):
    number_of_spoken_words = 0
    for speech in speeches:
        # count spaces and add 1
        number_of_spoken_words += (speech.count(' ') + 1)
    
    return number_of_spoken_words


def save_person_number_of_spoken_words(person, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    speeches = Speech.objects.filter_valid_speeches(
        timestamp
    ).filter(
        speaker=person
    ).values_list(
        'lemmatized_content',
        flat=True
    )

    PersonNumberOfSpokenWords(
        person=person,
        value=calculate_number_of_spoken_words(speeches),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()

def save_people_number_of_spoken_words(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_number_of_spoken_words(person, playing_field, timestamp)

def save_people_number_of_spoken_words_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_people_number_of_spoken_words(playing_field, timestamp=day)

def save_sparse_people_number_of_spoken_words_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_number_of_spoken_words(playing_field, timestamp=day)
