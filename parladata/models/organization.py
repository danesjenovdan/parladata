from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.models.link import Link
from parladata.models.person import Person
from parladata.models.memberships import PersonMembership, OrganizationMembership
from parladata.models.ballot import Ballot
from parladata.behaviors.models import (
    Timestampable,
    Taggable,
    Parsable,
    Sluggable,
    VersionableFieldsOwner
)
from colorfield.fields import ColorField

CLASSIFICATIONS = [
    ('root', 'root'),
    ('pg', 'pg'),
    ('commission', 'commission'),
    ('committee', 'committee'),
    ('council', 'council'),
    ('delegation', 'delegation'),
    ('friendship_group', 'friendship_group'),
    ('investigative_commission', 'investigative_commission'),
    ('other', 'other'),
]


class Organization(Timestampable, Taggable, Parsable, Sluggable, VersionableFieldsOwner):
    """A group with a common purpose or reason
    for existence that goes beyond the set of people belonging to it.
    """
    gov_id = models.TextField(_('Gov website ID'),
                              blank=True, null=True,
                              help_text=_('Gov website ID'))

    classification = models.TextField(_('classification'),
                                      blank=True, null=True,
                                      help_text=('An organization category, e.g. committee'),
                                      choices=CLASSIFICATIONS,)

    # reference to "http://popoloproject.com/schemas/organization.json#"
    parent = models.ForeignKey('Organization',
                               blank=True, null=True,
                               related_name='children',
                               on_delete=models.CASCADE,
                               help_text=_('The organization that contains this organization'))

    founding_date = models.DateTimeField(blank=True, null=True,
                                        help_text=_('A date of founding'))

    dissolution_date = models.DateTimeField(blank=True, null=True,
                                           help_text=_('A date of dissolution'))

    description = models.TextField(blank=True, null=True,
                                   help_text='Organization description')

    color = ColorField(default='#09a2cc')

    @property
    def name(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='OrganizationName',
            datetime=datetime.now()
        )

    @property
    def acronym(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='OrganizationAcronym',
            datetime=datetime.now()
        )

    @property
    def email(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='OrganizationEmail',
            datetime=datetime.now()
        )

    # TODO make all membership queries depend on a date
    def number_of_members_at(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return PersonMembership.valid_at(timestamp).filter(organization=self).distinct('member').count()

    def number_of_organization_members_at(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return OrganizationMembership.valid_at(timestamp).filter(organization=self).distinct('member').count()

    def number_of_voters_at(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return PersonMembership.valid_at(timestamp).filter(organization=self, role='voter').distinct('member').count()

    def number_of_organization_voters_at(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return OrganizationMembership.valid_at(timestamp).filter(organization=self, role='voter').distinct('member').count()

    @property
    def has_voters(self):
        return bool(self.memberships.filter(role='voter'))

    # TODO maybe we need to run distinct here
    def query_members(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        member_ids = PersonMembership.valid_at(timestamp).filter(organization=self).values_list('member', flat=True)
        return Person.objects.filter(
            id__in=member_ids
        )

    # we need this to get all the timestamps
    # of all the memberships before a given date
    #
    # why? to query speeches only for the time
    # when the speaker was a voter member of the organization
    def query_memberships_before(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return PersonMembership.valid_before(
            timestamp
        ).filter(
            on_behalf_of=self,
            role='voter'
        )

    def query_organization_members(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        member_ids = OrganizationMembership.valid_at(
            timestamp
        ).filter(
            organization=self
        ).values(
            'member'
        )

        return Organization.objects.filter(
            id__in=member_ids
        )

    def query_parliamentary_groups(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        # sometimes we have groups without members
        # this crashes some serializers (like vote/single
        # because it can't calculate the max_option for all groups)
        # so if a group has no members it should be filtered out

        ids_of_groups_with_voters = PersonMembership.objects.filter(
            models.Q(start_time__lte=timestamp) | models.Q(start_time__isnull=True),
            models.Q(end_time__gte=timestamp) | models.Q(end_time__isnull=True),
            organization__in=Organization.objects.filter(classification='pg'),  # TODO rename to parliamentary_group
        ).values_list('organization__id', flat=True).distinct('organization__id')

        return self.query_organization_members(timestamp).filter(id__in=ids_of_groups_with_voters)

    def query_voters(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return self.query_members_by_role('voter', timestamp)

    def query_members_by_role(self, role, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        member_ids = PersonMembership.valid_at(timestamp).filter(
            organization=self,
            role=role
        ).values_list('member', flat=True)

        return Person.objects.filter(
            id__in=member_ids
        )

    def query_organizations_by_role(self, role, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        member_ids = OrganizationMembership.valid_at(timestamp).filter(
            organization=self,
            role=role
        ).values_list('member', flat=True)

        return Organization.objects.filter(
            id__in=member_ids
        )

    def __str__(self):
        return f'{self.name} {self.id} {self.acronym}'

    def query_ballots_on_vote(self, vote):
        voter_ids = self.query_voters(vote.timestamp)
        return Ballot.objects.filter(vote=vote, personvoter__in=voter_ids)
