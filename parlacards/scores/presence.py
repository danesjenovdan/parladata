from datetime import datetime

from parladata.models.ballot import Ballot

from parlacards.models import PersonPresenceOnVotes

from parlacards.scores.common import get_dates_between, get_fortnights_between


def calculate_person_presence_on_votes(person, timestamp=datetime.now()):
    person_ballots = Ballot.objects.filter(
        personvoter=person,
        vote__timestamp__lte=timestamp
    )
    all_ballots = person_ballots.count()
    present_ballots = person_ballots.exclude(option='absent').count()
    if all_ballots == 0:
        return 0
    else:
        return present_ballots * 100 / all_ballots

def save_person_presence_on_votes(person, playing_field, timestamp=datetime.now()):
    PersonPresenceOnVotes(
        person=person,
        value=calculate_person_presence_on_votes(person, timestamp),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()

def save_people_presence_on_votes(playing_field, timestamp=datetime.now()):
    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_presence_on_votes(person, playing_field, timestamp)

def save_people_presence_on_votes_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_people_presence_on_votes(playing_field, timestamp=day)

def save_sparse_people_presence_on_votes_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_presence_on_votes(playing_field, timestamp=day)

