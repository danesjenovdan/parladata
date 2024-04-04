from django.conf import settings

from parladata.models.memberships import OrganizationMembership, PersonMembership

import math

from icu import Collator, Locale


local_collator = Collator.createInstance(Locale(settings.LANGUAGE_CODE))


def get_playing_fields(timestamp):
    organization_memberships = (
        OrganizationMembership.valid_at(timestamp)
        .filter(member__classification="root")
        .distinct("member")
    )

    return [
        organization_membership.member
        for organization_membership in organization_memberships
    ]


def truncate_score(score):
    trunc_factor = 10**5
    try:
        score = math.trunc(score * trunc_factor) / trunc_factor
    except:
        score = 0
    return score
