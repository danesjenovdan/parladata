from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from parladata.behaviors.models import Timestampable, Taggable, Parsable, Sluggable, VersionableFieldsOwner

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

    # array of items referencing "http://popoloproject.com/schemas/contact_detail.json#"
    description = models.TextField(blank=True, null=True,
                                   help_text='Organization description')

    def __str__(self):
        return self.name + " " + str(self.id) + " " + (self.acronym if self.acronym else '')

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
    def has_voters(self):
        if self.memberships.filter(role='voter'):
            return True
        else:
            return False
