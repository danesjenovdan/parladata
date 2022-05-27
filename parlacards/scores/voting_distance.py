from itertools import combinations

from datetime import datetime

from django.db.models import Count, Max

from parladata.models.ballot import Ballot
from parladata.models.vote import Vote
from parladata.models.memberships import PersonMembership

from parlacards.models import VotingDistance, GroupVotingDistance

from parlacards.scores.common import get_dates_between, get_fortnights_between, get_mandate_of_playing_field


def assign_value_to_option_string(option_string):
    return {
        'for': 1,
        'against': -1,
        'abstain': 0,
        'absent': 0,
        'did not vote': 0,
    }[option_string]

# implement this with numpy
# IF AND ONLY IF we need
# numpy someplace else
def euclidean(v1, v2):
    return sum((p-q)**2 for p, q in zip(v1, v2)) ** .5

#
# PERSON
#
def calculate_voting_distance(from_person, to_person, mandate, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    from_ballots = Ballot.objects.filter(
        personvoter=from_person,
        vote__timestamp__lte=timestamp,
        vote__motion__session__mandate=mandate
    )

    to_ballots = Ballot.objects.filter(
        personvoter=to_person,
        vote__timestamp__lte=timestamp,
        vote__motion__session__mandate=mandate,
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

def save_voting_distance(from_person, to_person, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = get_mandate_of_playing_field(playing_field)

    VotingDistance(
        person=from_person,
        target=to_person,
        value=calculate_voting_distance(from_person, to_person, mandate, timestamp),
        timestamp=timestamp,
        playing_field=playing_field
    ).save()

def save_voting_distances(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = get_mandate_of_playing_field(playing_field)

    people = playing_field.query_voters(timestamp)
    pairs = combinations(people, 2)

    for pair in pairs:
        distance = calculate_voting_distance(pair[0], pair[1], mandate, timestamp)
        
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

def save_voting_distances_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_voting_distances(playing_field, timestamp=day)

def save_sparse_voting_distances_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_voting_distances(playing_field, timestamp=day)

#
# GROUP
#

def calculate_group_voting_distance(group, playing_field, mandate, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    # get all relevant votes
    votes = Vote.objects.filter(
        timestamp__lte=timestamp,
        motion__session__mandate=mandate
    ).order_by(
        '-timestamp'
    )

    # dictionary to contain the output
    # keys are person ids and values are
    # distances to the party
    output = {}

    party_ballots = []
    excluded_vote_ids = []

    # calculate party_ballots and excluded_vote_ids
    for vote in votes:
        # get relevant voters
        voters = PersonMembership.valid_at(vote.timestamp).filter(
            on_behalf_of=group,
            role='voter'
        )

        # if a vote did not have a group participating
        # add the vote to the exclusion list and continue
        if voters.count() == 0:
            excluded_vote_ids.append(vote.id)
            continue

        ballots = Ballot.objects.filter(
            vote=vote,
            personvoter__in=voters.values_list('member_id', flat=True)
        ).exclude(
            # TODO Filip would remove this
            # because when everyone is absent
            # this voting event will not have
            # a max option but this needs
            # consultation with product people
            option='absent'
        )

        options_aggregated = ballots.values(
            'option'
        ).annotate(
            dcount=Count('option')
        ).order_by().aggregate(Max('option'))
        # If you don't include the order_by(),
        # you may get incorrect results if the
        # default sorting is not what you expect.

        if not options_aggregated['option__max']:
            excluded_vote_ids.append(vote.id)
            continue

        party_ballots.append(options_aggregated['option__max'])

    # calculate party_coordinates
    party_coordinates = [
        assign_value_to_option_string(option_string) for
        option_string in party_ballots
    ]

    # get all voters who are not group members
    excluded_voters = group.query_members(timestamp)
    relevant_voters = playing_field.query_voters(
        timestamp
    ).exclude(
        id__in=excluded_voters.values('id')
    )

    for person in relevant_voters:
        # get personal ballots and exclude the ones
        # that were problematic on the party level
        person_ballots = Ballot.objects.filter(
            personvoter=person,
            vote__timestamp__lte=timestamp
        ).exclude(
            vote__id__in=excluded_vote_ids
        )

        person_coordinates = [
            assign_value_to_option_string(option_string) for
            option_string in person_ballots.values_list('option', flat=True)
        ]

        output[person.id] = euclidean(person_coordinates, party_coordinates)

    return output

def save_group_voting_distance(group, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = get_mandate_of_playing_field(playing_field)

    distances = calculate_group_voting_distance(group, playing_field, mandate)

    for person_id in distances.keys():
        GroupVotingDistance(
            group=group,
            target_id=person_id,
            value=distances[person_id],
            timestamp=timestamp,
            playing_field=playing_field
        ).save()

def save_groups_voting_distances(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    groups = playing_field.query_parliamentary_groups(timestamp)
    for group in groups:
        save_group_voting_distance(group, playing_field, timestamp)

def save_groups_voting_distances_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_voting_distances(playing_field, timestamp=day)

def save_sparse_groups_voting_distances_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_voting_distances(playing_field, timestamp=day)









# TODO this is not used, but still interesting
# leaving it here in case we persuade product people this is interesting
def calculate_voting_distance_between_groups(from_group, to_group, mandate, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    # get all relevant votes
    votes = Vote.objects.filter(
        timestamp__lte=timestamp,
        motion__session__mandate=mandate
    ).order_by(
        '-timestamp'
    )

    from_party_ballots = []
    to_party_ballots = []

    for vote in votes:
        # get relevant voters
        from_voters = PersonMembership.valid_at(vote.timestamp).filter(
            on_behalf_of=from_group,
            role='voter'
        )
        to_voters = PersonMembership.valid_at(vote.timestamp).filter(
            on_behalf_of=to_group,
            role='voter'
        )

        # if a vote did not have a group participating continue
        if (from_voters.count() == 0) or (to_voters.count() == 0):
            continue

        from_ballots = Ballot.objects.filter(
            vote=vote,
            personvoter__in=from_voters.values_list('member_id', flat=True)
        ).exclude(
            # TODO Filip would remove this
            # because when everyone is absent
            # this voting event will not have
            # a max option but this needs
            # consultation with product people
            option='absent'
        )

        to_ballots = Ballot.objects.filter(
            vote=vote,
            personvoter__in=to_voters.values_list('member_id', flat=True)
        ).exclude(
            # TODO Filip would remove this
            # because when everyone is absent
            # this voting event will not have
            # a max option but this needs
            # consultation with product people
            option='absent'
        )

        from_options_aggregated = from_ballots.values(
            'option'
        ).annotate(
            dcount=Count('option')
        ).order_by().aggregate(Max('option'))
        # If you don't include the order_by(),
        # you may get incorrect results if the
        # default sorting is not what you expect.

        to_options_aggregated = to_ballots.values(
            'option'
        ).annotate(
            dcount=Count('option')
        ).order_by().aggregate(Max('option'))
        # If you don't include the order_by(),
        # you may get incorrect results if the
        # default sorting is not what you expect.

        if not (from_options_aggregated['option__max'] and to_options_aggregated['option__max']):
            continue

        from_party_ballots.append(from_options_aggregated['option__max'])
        to_party_ballots.append(to_options_aggregated['option__max'])

    from_coordinates = [
        assign_value_to_option_string(option_string) for
        option_string in from_party_ballots
    ]
    to_coordinates = [
        assign_value_to_option_string(option_string) for
        option_string in to_party_ballots
    ]

    return euclidean(from_coordinates, to_coordinates)

def save_voting_distance_between_groups(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = get_mandate_of_playing_field(playing_field)

    groups = playing_field.query_parliamentary_groups(timestamp)
    pairs = combinations(groups, 2)

    for pair in pairs:
        distance = calculate_group_voting_distance(pair[0], pair[1], mandate, timestamp)

        GroupVotingDistance(
            group=pair[0],
            target=pair[1],
            value=distance,
            timestamp=timestamp,
            playing_field=playing_field
        ).save()

        GroupVotingDistance(
            group=pair[1],
            target=pair[0],
            value=distance,
            timestamp=timestamp,
            playing_field=playing_field
        ).save()
