from datetime import datetime

from django.db.models.functions import TruncMonth
from django.db.models import Count

from parladata.models.ballot import Ballot
from parladata.models.vote import Vote

from parlacards.models import PersonMonthlyPresenceOnVote

from parlacards.scores.common import get_dates_between, get_fortnights_between

def calculate_person_monthly_presence_on_votes(person, playing_field, timestamp=datetime.now()):
    """
    Returns monthly ballots count of voter
    """

    data = []

    ballots = Ballot.objects.filter(
        personvoter=person,
        vote__timestamp__lte=timestamp
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
        motion__session__organizations=playing_field
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

def save_person_monthly_presence_on_votes(person, playing_field, timestamp=datetime.now()):
    monthly_results = calculate_person_monthly_presence_on_votes(person, playing_field, timestamp)
    for result in monthly_results:
        if result['total'] > 0:
            present_count = result['for'] + result['abstain'] + result['against']
            person_votes_count = present_count + result['absent']

            no_mandate = (result['total'] - person_votes_count) * 100 / result['total']
            present = present_count * 100 / result['total']

            score = PersonMonthlyPresenceOnVote.objects.filter(
                person=person,
                timestamp=result['timestamp'],
                playing_field=playing_field
            ).first()

            if score:
                score.no_mandate=no_mandate
                score.present=present
                score.save()
            else:
                PersonMonthlyPresenceOnVote(
                    person=person,
                    value=present,
                    no_mandate=no_mandate,
                    timestamp=result['timestamp'],
                    playing_field=playing_field,
                ).save()

def save_people_monthly_presence_on_votes(playing_field, timestamp=datetime.now()):
    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_monthly_presence_on_votes(person, playing_field, timestamp)

def save_people_monthly_presence_on_votes_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_people_monthly_presence_on_votes(playing_field, timestamp=day)

def save_sparse_people_monthly_presence_on_votes_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_monthly_presence_on_votes(playing_field, timestamp=day)
