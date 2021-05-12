from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from parladata.models.link import Link
from parladata.models.person import Person
from parladata.models.memberships import PersonMembership, OrganizationMembership
from parladata.behaviors.models import (
    Timestampable,
    Taggable,
    Parsable,
    Sluggable,
    VersionableFieldsOwner
)

class Organization(Timestampable, Taggable, Parsable, Sluggable, VersionableFieldsOwner):
    """A group with a common purpose or reason
    for existence that goes beyond the set of people belonging to it.
    """
    gov_id = models.TextField(_('Gov website ID'),
                              blank=True, null=True,
                              help_text=_('Gov website ID'))

    classification = models.TextField(_('classification'),
                                      blank=True, null=True,
                                      help_text=('An organization category, e.g. committee'))

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

    @property
    def name(self):
        return self.versionable_property_on_date(
            owner=self,
            property_model_name='OrganizationName',
            datetime=datetime.now()
        )

    @property
    def acronym(self):
        return self.versionable_property_on_date(
            owner=self,
            property_model_name='OrganizationAcronym',
            datetime=datetime.now()
        )

    @property
    def email(self):
        return Link.objects.filter(
            organization=self,
            note='email'
        ).first()
    
    @property
    def number_of_members(self):
        return PersonMembership.objects.filter(organization=self).distinct('member').count()
    
    @property
    def number_of_organization_members(self):
        return OrganizationMembership.objects.filter(organization=self).distinct('member').count()
    
    @property
    def number_of_voters(self):
        return PersonMembership.objects.filter(organization=self, role='voter').distinct('member').count()
    
    @property
    def number_of_organization_voters(self):
        return OrganizationMembership.objects.filter(organization=self, role='voter').distinct('member').count()

    @property
    def has_voters(self):
        return bool(self.memberships.filter(role='voter'))

    @property
    def members(self):
        member_ids = PersonMembership.objects.filter(organization=self).values_list('member', flat=True)
        return Person.objects.filter(
            id__in=member_ids
        )

    def query_people_by_role(self, role=None):    
        member_ids = PersonMembership.objects.filter(organization=self, role=role).values_list('member', flat=True)
        return Person.objects.filter(
            id__in=member_ids
        )

    def __str__(self):
        return self.name + " " + str(self.id) + " " + (self.acronym if self.acronym else '')
