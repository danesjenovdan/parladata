from parladata.models import Session, Speech, Vote
from parladata.update_utils import send_email

from django.db.models import Count
from django.contrib.auth.models import Group
from django.conf import settings


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
        try:
            org = v.motion.session.organizations.first()
        except:
            invalid_votes.append(v)
            continue
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

def run_tests():
    duplicated_sessions = check_for_duplicated_sessions()
    duplicated_votes = check_for_duplicated_votes()
    invalid_votes = check_num_of_ballots_per_vote()
    duplicated_speeches = check_for_duplicated_speeches()

    parser_permission_group = Group.objects.filter(name__icontains="parser_owners").first()

    assert bool(parser_permission_group), 'There\'s no parser owners permission group'

    if duplicated_sessions or duplicated_votes or check_num_of_ballots_per_vote or check_for_duplicated_speeches:
        for parser_owner in parser_permission_group.user_set.all():
            send_email(
                f'On parlameter {settings.BASE_URL} is some data corruption',
                parser_owner.email,
                'data_validation_email.html',
                {
                    'base_url': settings.BASE_URL,
                    'duplicated_sessions': duplicated_sessions,
                    'duplicated_votes': duplicated_votes,
                    'invalid_votes': invalid_votes,
                    'duplicated_speeches': duplicated_speeches
                }
            )
