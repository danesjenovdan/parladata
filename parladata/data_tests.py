from parladata.models import Session, Speech, Vote
from django.db.models import Count


def check_for_duplicated_sessions():
    """
    Test whether there are sessions of the same organization with the same name
    """
    duplicated_sessions = Session.objects.values(
        'name',
        'organizations'
    ).annotate(same_name=Count('name')).filter(same_name__gt=1)
    return duplicated_sessions

def check_for_duplicated_votes():
    """
    Test whether there are vote with the same name and timestamp
    """
    duplicated_votes = Vote.objects.values('name', 'timestamp').annotate(same_name=Count('name')).filter(same_name__gt=1)
    return duplicated_votes

def check_num_of_ballots_per_vote():
    """
    Test whether there is a vote where there is no correct number of ballots in relation to the number of voters.
    """
    invalid_votes = []
    vv = Vote.objects.all()
    for v in vv:
        org = v.motion.session.organizations.first()
        number_of_voters = org.number_of_voters_at(timestamp=v.timestamp)
        count = v.ballots.count()
        if count != number_of_voters:
            invalid_votes.append(v)
    return invalid_votes

def check_for_duplicated_speeches():
    """
    Test whether there are duplicated speech.
    """
    duplicated_speeches = Speech.objects.values(
        'content',
        'speaker',
        'session',
        'start_time',
        'order'
    ).annotate(same_name=Count('content')).filter(same_name__gt=1)
    return duplicated_speeches
