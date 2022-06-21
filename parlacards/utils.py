from django.conf import settings

from parladata.models.memberships import OrganizationMembership, PersonMembership

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
