from datetime import datetime

from django.db.models.functions import TruncMonth
from django.db.models import Count, Q

from parladata.models.ballot import Ballot
from parladata.models.vote import Vote
from parladata.models.common import Mandate

from parlacards.models import PersonMonthlyVoteAttendance, GroupMonthlyVoteAttendance

from parlacards.scores.common import get_dates_between, get_fortnights_between

def calculate_person_monthly_vote_attendance(person, playing_field, timestamp=None):
    """
    Returns monthly ballots count of voter
    """
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    data = []

    ballots = Ballot.objects.filter(
        personvoter=person,
        vote__timestamp__lte=timestamp,
        vote__motion__session__mandate=mandate
    ).annotate(
        month=TruncMonth('vote__timestamp')
    ).values(
        'month',
        'option'
    ).annotate(
        ballot_count=Count('option')
    ).order_by(
        'month'
    )

    votes = Vote.objects.filter(
        timestamp__lte=timestamp,
        motion__session__organizations=playing_field,
        motion__session__mandate=mandate
    ).exclude(
        ballots__isnull=True
    ).annotate(
        month=TruncMonth('timestamp')
    ).values(
        'month'
    ).annotate(
        total_votes=Count('id')
    ).order_by(
        'month'
    )

    for month in votes:
        temp_data = {
            'timestamp': month['month'].isoformat(),
            'absent': 0,
            'abstain': 0,
            'for': 0,
            'against': 0,
            'total': month['total_votes']
        }

        monthly_sums = ballots.filter(month=month['month'])
        for sums in monthly_sums:
            temp_data[sums['option']] = sums['ballot_count']

        data.append(temp_data)

    return data

def save_person_monthly_vote_attendance(person, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    monthly_results = calculate_person_monthly_vote_attendance(person, playing_field, timestamp)
    for result in monthly_results:
        if result['total'] > 0:
            present_count = result['for'] + result['abstain'] + result['against']
            person_votes_count = present_count + result['absent']

            no_mandate = (result['total'] - person_votes_count) * 100 / result['total']
            present = present_count * 100 / result['total']

            score = PersonMonthlyVoteAttendance.objects.filter(
                person=person,
                timestamp=result['timestamp'],
                playing_field=playing_field
            ).first()

            if score:
                score.no_mandate=no_mandate
                score.value=present
                score.save()
            else:
                PersonMonthlyVoteAttendance(
                    person=person,
                    value=present,
                    no_mandate=no_mandate,
                    timestamp=result['timestamp'],
                    playing_field=playing_field,
                ).save()

def save_people_monthly_vote_attendance(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_monthly_vote_attendance(person, playing_field, timestamp)

def save_people_monthly_vote_attendance_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_people_monthly_vote_attendance(playing_field, timestamp=day)

def save_sparse_people_monthly_vote_attendance_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_monthly_vote_attendance(playing_field, timestamp=day)


# GROUPS

def calculate_group_monthly_vote_attendance(group, playing_field, timestamp=None):
    """
    Returns monthly ballots count of voter
    """
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    memberships = group.query_memberships_before(timestamp)
    member_ids = memberships.values_list('member_id', flat=True).distinct('member_id')

    ballots = Ballot.objects.none()
    all_valid_ballots = Ballot.objects.none()

    for member_id in member_ids:
        member_ballots = Ballot.objects.filter(
            vote__timestamp__lte=timestamp,
            personvoter__id=member_id,
            vote__motion__session__mandate=mandate
        )

        member_memberships = memberships.filter(
            member__id=member_id
        ).values(
            'start_time',
            'end_time'
        )
        q_objects = Q()
        for membership in member_memberships:
            q_params = {}
            if membership['start_time']:
                q_params['vote__timestamp__gte'] = membership['start_time']
            if membership['end_time']:
                q_params['vote__timestamp__lte'] = membership['end_time']
            q_objects.add(
                Q(**q_params),
                Q.OR
            )

        all_valid_ballots = all_valid_ballots.union(member_ballots.filter(q_objects))

    all_valid_ballots_ids = all_valid_ballots.values('id')

    annotated_ballots = Ballot.objects.filter(
        id__in=all_valid_ballots_ids
    ).annotate(
        month=TruncMonth('vote__timestamp')
    ).values(
        'month',
        'option'
    ).annotate(
        ballot_count=Count('option')
    ).order_by(
        'month'
    )
    data = {}
    for annotated_ballot in annotated_ballots:
        if not annotated_ballot['month'].isoformat() in data.keys():
            data[annotated_ballot['month'].isoformat()] = {
                'absent': 0,
                'abstain': 0,
                'for': 0,
                'against': 0,
            }
        data[annotated_ballot['month'].isoformat()][annotated_ballot['option']] = annotated_ballot['ballot_count']

    return data

def save_group_monthly_vote_attendance(group, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    monthly_results = calculate_group_monthly_vote_attendance(group, playing_field, timestamp)
    for month, result in monthly_results.items():
        present_count = result['for'] + result['abstain'] + result['against']
        group_votes_count = present_count + result['absent']

        no_mandate = 0
        present = present_count * 100 / group_votes_count

        score = GroupMonthlyVoteAttendance.objects.filter(
            group=group,
            timestamp=month,
            playing_field=playing_field
        ).first()

        if score:
            score.no_mandate=no_mandate
            score.value=present
            score.save()
        else:
            GroupMonthlyVoteAttendance(
                group=group,
                value=present,
                no_mandate=no_mandate,
                timestamp=month,
                playing_field=playing_field,
            ).save()

def save_groups_monthly_vote_attendance(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    groups = playing_field.query_parliamentary_groups(timestamp)

    for group in groups:
        save_group_monthly_vote_attendance(group, playing_field, timestamp)

def save_groups_monthly_vote_attendance_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_monthly_vote_attendance(playing_field, timestamp=day)

def save_sparse_groups_monthly_vote_attendance_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_monthly_vote_attendance(playing_field, timestamp=day)
