from datetime import datetime

from django.db.models import Q

from collections import Counter

from parladata.models.ballot import Ballot

from parlacards.models import PersonVoteAttendance, GroupVoteAttendance
from parlacards.scores.common import get_dates_between, get_fortnights_between


def calculate_person_vote_attendance(person, timestamp=datetime.now()):
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

def save_person_vote_attendance(person, playing_field, timestamp=datetime.now()):
    PersonVoteAttendance(
        person=person,
        value=calculate_person_vote_attendance(person, timestamp),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()

def save_people_vote_attendance(playing_field, timestamp=datetime.now()):
    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_vote_attendance(person, playing_field, timestamp)

def save_people_vote_attendance_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_people_vote_attendance(playing_field, timestamp=day)

def save_sparse_people_vote_attendance_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_vote_attendance(playing_field, timestamp=day)


# Group
def calculate_group_vote_attendance(group, timestamp=datetime.now()):
    memberships = group.query_memberships_before(timestamp)
    member_ids = memberships.values_list('member_id', flat=True).distinct('member_id')

    ballots = Ballot.objects.none()

    for member_id in member_ids:
        member_ballots = Ballot.objects.filter(
            personvoter_id=member_id,
            vote__timestamp__lte=timestamp,
        )

        member_memberships = memberships.filter(
            member__id=member_id
        ).values(
            'start_time',
            'end_time'
        )

        q_ballot_objects = Q()

        for membership in member_memberships:
            q_ballots_params = {}
            if membership['start_time']:
                q_ballots_params['vote__timestamp__gte'] = membership['start_time']
            if membership['end_time']:
                q_ballots_params['vote__timestamp__lte'] = membership['end_time']
            q_ballot_objects.add(
                Q(**q_ballots_params),
                Q.OR
            )

        ballots = ballots.union(member_ballots.filter(q_ballot_objects))

    ballot_options = ballots.values_list('option', flat=True)
    option_counter = Counter(ballot_options)

    ballots_for = option_counter.get('for', 0)
    ballots_against = option_counter.get('against', 0)
    ballots_abstain = option_counter.get('abstain', 0)
    ballots_absent = option_counter.get('absent', 0)

    present_ballots = ballots_for + ballots_against + ballots_abstain
    all_ballots = present_ballots + ballots_absent
    if all_ballots == 0:
        return 0
    else:
        return present_ballots * 100 / all_ballots

def save_group_vote_attendance(group, playing_field, timestamp=datetime.now()):
    GroupVoteAttendance(
        group=group,
        value=calculate_group_vote_attendance(group, timestamp),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()

def save_groups_vote_attendance(playing_field, timestamp=datetime.now()):
    groups = playing_field.query_parliamentary_groups(timestamp)

    for group in groups:
        save_group_vote_attendance(group, playing_field, timestamp)

def save_groups_vote_attendance_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_vote_attendance(playing_field, timestamp=day)

def save_sparse_groups_vote_attendance_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_vote_attendance(playing_field, timestamp=day)
