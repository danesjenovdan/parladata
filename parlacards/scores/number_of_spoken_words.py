from datetime import datetime

from parladata.models.speech import Speech
from parladata.models.memberships import PersonMembership
from parladata.models.person import Person

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


def save_person_number_of_spoken_words(person, playing_field, timestamp=datetime.now()):
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

def save_people_number_of_spoken_words(playing_field, timestamp=datetime.now()):
    people = playing_field.query_voters(timestamp)

    # TODO this is mostly copied from parlacards.scores.avg_number_of_speeches_per_session
    # if a leader exists he should be a competitor as well
    # TODO this is a very broad filter, it will probably
    # need to be reworked into something more precise
    leader_ids = PersonMembership.objects.filter(
        role='leader'
    ).order_by(
        'id'
    ).values_list(
        'member__id',
        flat=True
    )
    leaders = Person.objects.filter(id__in=leader_ids)
    # TODO maybe all of this should be exempt from here
    # and we should have separate functions for calculating
    # leader scores

    for person in people.union(leaders):
        save_person_number_of_spoken_words(person, playing_field, timestamp)

def save_people_number_of_spoken_words_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_people_number_of_spoken_words(playing_field, timestamp=day)

def save_sparse_people_number_of_spoken_words_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_number_of_spoken_words(playing_field, timestamp=day)
