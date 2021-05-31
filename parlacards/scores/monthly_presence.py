from datetime import datetime

from django.db.models.functions import TruncMonth
from django.db.models import Count

from parladata.models.ballot import Ballot
from parladata.models.vote import Vote

from parlacards.models import PersonMonthlyPresenceOnVote


def calculate_person_monthly_presence_on_votes(person, playing_field, timestamp=datetime.now()):
    """
    Returns monthly ballots count of voter
    """

    data = []

    ballots = Ballot.objects.filter(
        personvoter=person,
        vote__timestamp__lte=timestamp
    )

    ballots = ballots.annotate(month=TruncMonth('vote__timestamp')).values('month', 'option')
    ballots = ballots.annotate(ballot_count=Count('option')).order_by('month')

    votes = Vote.objects.filter(
        timestamp__lte=timestamp,
        motion__session__organizations=playing_field
    )

    votes = votes.annotate(month=TruncMonth('timestamp')).values('month')
    votes = votes.annotate(total_votes=Count('id')).order_by("month")

    for month in votes:
        date_ = month['month']
        total = month['total_votes']

        temp_data = {
            'timestamp': date_.isoformat(),
            'absent': 0,
            'abstain': 0,
            'for': 0,
            'against': 0,
            'total': total
        }

        sums_of_month = ballots.filter(month=date_)
        for sums in sums_of_month:
            temp_data[sums['option']] = sums['ballot_count']

        data.append(temp_data)

    return data

def save_person_monthly_presence_on_votes(person, playing_field, timestamp=datetime.now()):
    results = calculate_person_monthly_presence_on_votes(person, playing_field, timestamp)
    for result in results:
        if result['total'] > 0:
            present_count = result['for'] + result['abstain'] + result['against']
            person_votes_count = present_count + result['absent']

            no_mandate = (result['total'] - person_votes_count) * 100 / result['total']
            present = present_count * 100 / result['total']

            analize = PersonMonthlyPresenceOnVote.objects.filter(
                person=person,
                timestamp=result['timestamp'],
                playing_field=playing_field
            ).first()
            if analize:
                analize.no_mandate=no_mandate
                analize.present=present
                analize.save()
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
