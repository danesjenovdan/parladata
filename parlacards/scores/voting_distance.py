from itertools import combinations

from datetime import datetime

from parladata.models.ballot import Ballot

from parlacards.models import VotingDistance

from parlacards.scores.common import get_dates_between, get_fortnights_between

def assign_value_to_option_string(option_string):
    return {
        'for': 1,
        'against': -1,
        'abstain': 0,
        'absent': 0,
    }[option_string]

# implement this with numpy
# IF AND ONLY IF we need
# numpy someplace else
def euclidean(v1, v2):
    return sum((p-q)**2 for p, q in zip(v1, v2)) ** .5

def calculate_voting_distance(from_person, to_person, timestamp=datetime.now()):
    from_ballots = Ballot.objects.filter(
        personvoter=from_person,
        vote__timestamp__lte=timestamp
    )

    to_ballots = Ballot.objects.filter(
        personvoter=to_person,
        vote__timestamp__lte=timestamp
    )

    # we will only calculate the distance for voting events
    # where both from_person and to_person participated
    vote_ids_intersection = set(
        from_ballots.values_list(
            'vote_id',
            flat=True
        )
    ).intersection(
        set(
            to_ballots.values_list(
                'vote_id',
                flat=True,
            )
        )
    )

    filtered_from_ballots = from_ballots.filter(vote__id__in=vote_ids_intersection).order_by('vote__id')
    filtered_to_ballots = to_ballots.filter(vote__id__in=vote_ids_intersection).order_by('vote__id')

    from_coordinates = [assign_value_to_option_string(option_string) for option_string in filtered_from_ballots.values_list('option', flat=True)]
    to_coordinates = [assign_value_to_option_string(option_string) for option_string in filtered_to_ballots.values_list('option', flat=True)]

    return euclidean(from_coordinates, to_coordinates)

def save_voting_distance(from_person, to_person, playing_field, timestamp=datetime.now()):
    VotingDistance(
        person=from_person,
        target=to_person,
        value=calculate_voting_distance(from_person, to_person, timestamp),
        timestamp=timestamp,
        playing_field=playing_field
    ).save()

def save_voting_distances(playing_field, timestamp=datetime.now()):
    people = playing_field.query_voters(timestamp)
    pairs = combinations(people, 2)

    for pair in pairs:
        distance = calculate_voting_distance(pair[0], pair[1], timestamp)
        
        VotingDistance(
            person=pair[0],
            target=pair[1],
            value=distance,
            timestamp=timestamp,
            playing_field=playing_field
        ).save()

        VotingDistance(
            person=pair[1],
            target=pair[0],
            value=distance,
            timestamp=timestamp,
            playing_field=playing_field
        ).save()

def save_voting_distances_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_voting_distances(playing_field, timestamp=day)

def save_sparse_voting_distances_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_voting_distances(playing_field, timestamp=day)
