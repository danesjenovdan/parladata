from parladata.models.memberships import OrganizationMembership


def get_organizations_from_mandate(mandate, date):
    membership = OrganizationMembership.valid_at(date).filter(mandate=mandate).first()
    if not membership:
        raise Exception(f'Root organization membership for this mandate does not exist')
    playing_field = membership.member
    root_organization = membership.organization
    return root_organization, playing_field
