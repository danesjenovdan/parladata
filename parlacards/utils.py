from django.conf import settings

from parladata.models.memberships import OrganizationMembership, PersonMembership

import math

from icu import Collator, Locale


local_collator = Collator.createInstance(Locale(settings.LANGUAGE_CODE))

def get_playing_fields(timestamp):
    person_memberships = PersonMembership.valid_at(timestamp).filter(
        role='voter'
    ).distinct('organization')

    return [
        person_membership.organization
        for person_membership
        in person_memberships
    ]


def truncate_score(score):
    trunc_factor = 10 ** 5
    try:
        score = math.trunc(score * trunc_factor) / trunc_factor
    except:
        score = 0
    return score
