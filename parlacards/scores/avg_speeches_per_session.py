from datetime import datetime

from parladata.models.speech import Speech
from parladata.models.ballot import Ballot

from parlacards.models import PersonAvgSpeechesPerSession

from parlacards.scores.common import get_dates_between, get_fortnights_between


def calculate_number_of_speeches_of_person(person, timestamp=datetime.now()):
    person_speeches = Speech.objects.filter_valid_speeches(timestamp).filter(speaker=person, start_time__lte=timestamp)
    num_of_speeches = person_speeches.count()

    ballot_sessions = list(Ballot.objects.filter(personvoter=person, vote__timestamp__lte=timestamp).distinct('vote__motion__session').values_list('vote__motion__session', flat=True))
    speech_sessions = list(person_speeches.distinct('session').values_list('session', flat=True))

    no_of_sessions_with_activity = len(set(ballot_sessions + speech_sessions))

    if no_of_sessions_with_activity  == 0:
        return 0
    else:
        return num_of_speeches / no_of_sessions_with_activity

def save_person_speeches_per_session(person, playing_field, timestamp=datetime.now()):
    PersonAvgSpeechesPerSession(
        person=person,
        value=calculate_number_of_speeches_of_person(person, timestamp),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()

def save_people_speeches_per_session(playing_field, timestamp=datetime.now()):
    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_speeches_per_session(person, playing_field, timestamp)

def save_people_speeches_per_session_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_person_speeches_per_session(playing_field, timestamp=day)

def save_sparse_people_speeches_per_session_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_person_speeches_per_session(playing_field, timestamp=day)
