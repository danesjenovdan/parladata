from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from parladata.behaviors.models import Timestampable, Taggable, Parsable

class OrganizationName(Timestampable, Parsable):
    """
    Objects for name history of organization.
    """
    organization = models.ForeignKey('Organization',
                                     help_text=_('The organization that holds this name.'),
                                     on_delete=models.CASCADE,
                                     related_name='names')

    name = models.TextField(_('name'),
                            help_text=_('A primary name, e.g. a legally recognized name'))

    acronym = models.CharField(_('acronym'),
                               blank=True,
                               null=True,
                               max_length=128,
                               help_text=_('Organization acronym'))

    start_time = models.DateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = models.DateTimeField(blank=True, null=True,
                                   help_text='End time')

    def __str__(self):
        return f'{self.name}'

class Organization(Timestampable, Taggable, Parsable):
    """A group with a common purpose or reason
    for existence that goes beyond the set of people belonging to it.
    """
    gov_id = models.TextField(_('Gov website ID'),
                              blank=True, null=True,
                              help_text=_('Gov website ID'))

    classification = models.CharField(_('classification'),
                                      max_length=128,
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

    def name_at_time(self, from_date_time=datetime.now()):
        name_instance = self.names.filter(models.Q(start_time__lte=from_date_time) |
                                 models.Q(start_time=None),
                                 models.Q(end_time__gte=from_date_time) |
                                 models.Q(end_time=None)).first()
        if name_instance:
            return name_instance.name

        raise Exception(f'Organization with id {self.id} has no name for this time.')

    def acronym_at_time(self, from_date_time=datetime.now()):
        name_instance = self.names.filter(models.Q(start_time__lte=from_date_time) |
                                          models.Q(start_time=None),
                                          models.Q(end_time__gte=from_date_time) |
                                          models.Q(end_time=None)).first()
        if name_instance:
            return name_instance.acronym
        
        raise Exception(f'Organization with id {self.id} has no name (and therefore acronyms) for this time.')

    @property
    def name(self):
        return self.name_at_time()

    @property
    def acronym(self):
        return self.acronym_at_time()

    @property
    def has_voters(self):
        if self.memberships.filter(role='voter'):
            return True
        else:
            return False
