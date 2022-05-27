from datetime import datetime

from parladata.models.session import Session
from parladata.models.speech import Speech
from parladata.models.ballot import Ballot

from parlacards.models import PersonAvgSpeechesPerSession

from parlacards.scores.common import get_dates_between, get_fortnights_between, get_mandate_of_playing_field


def calculate_person_avg_number_of_speeches(person, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = get_mandate_of_playing_field(playing_field)

    person_speeches = Speech.objects.filter_valid_speeches(timestamp).filter(
        speaker=person,
        session__mandate=mandate,
        start_time__lte=timestamp
    )
    num_of_speeches = person_speeches.count()

    ballot_session_ids = Ballot.objects.filter(
        personvoter=person,
        vote__motion__session__mandate=mandate,
        vote__timestamp__lte=timestamp
    ).distinct(
        'vote__motion__session__id'
    ).values_list(
        'vote__motion__session__id',
        flat=True
    )

    speech_session_ids = person_speeches.distinct(
        'session__id'
    ).values_list(
        'session__id',
        flat=True
    )

    no_of_sessions_with_activity = len(
        set(ballot_session_ids).union(
            set(speech_session_ids)
        )
    )

    if no_of_sessions_with_activity  == 0:
        return 0
    else:
        return num_of_speeches / no_of_sessions_with_activity

def save_person_avg_number_of_speeches_per_session(person, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    PersonAvgSpeechesPerSession(
        person=person,
        value=calculate_person_avg_number_of_speeches(person, playing_field, timestamp),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()

def save_people_avg_number_of_speeches_per_session(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_avg_number_of_speeches_per_session(person, playing_field, timestamp)

def save_people_avg_number_of_speeches_per_session_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_people_avg_number_of_speeches_per_session(playing_field, timestamp=day)

def save_sparse_people_avg_number_of_speeches_per_session_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_avg_number_of_speeches_per_session(playing_field, timestamp=day)
