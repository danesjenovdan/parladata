from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from parladata.behaviors.models import Timestampable, Taggable

class OrganizationName(Timestampable):
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

class Organization(Timestampable, Taggable, models.Model):
    """A group with a common purpose or reason
    for existence that goes beyond the set of people belonging to it.
    """

    name_parser = models.CharField(max_length=1024,
                                   help_text='Name for parser.',
                                   blank=True, null=True)

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

    dissolution_date = models.DateTimeField(blank=True, null=True,
                                           help_text=_('A date of dissolution'))

    founding_date = models.DateTimeField(blank=True, null=True,
                                        help_text=_('A date of founding'))

    # array of items referencing "http://popoloproject.com/schemas/contact_detail.json#"
    description = models.TextField(blank=True, null=True,
                                   help_text='Organization description')

    is_coalition = models.IntegerField(blank=True, null=True,
                                       help_text='1 if coalition, -1 if not, 0 if it does not apply')

    url_name = 'organization-detail'

    voters = models.IntegerField(_('voters'),
                                 blank=True,
                                 null=True,
                                 help_text='number of votes cast for this person in their district')

    def __str__(self):
        return self.name + " " + str(self.id) + " " + (self._acronym if self._acronym else '')


    def name_at_time(self, from_date_time=datetime.now()):
        name_instance = self.names.filter(models.Q(start_time__lte=from_date_time) |
                                 models.Q(start_time=None),
                                 models.Q(end_time__gte=from_date_time) |
                                 models.Q(end_time=None)).first()
        if name_instance:
            return name_instance.name

        raise Exception('This organization has no names for this time.')

    def acronym_at_time(self, from_date_time=datetime.now()):
        name_instance = self.names.filter(models.Q(start_time__lte=from_date_time) |
                                          models.Q(start_time=None),
                                          models.Q(end_time__gte=from_date_time) |
                                          models.Q(end_time=None)).first()
        if name_instance:
            return name_instance.acronym
        
        raise Exception('This organization has no names (and therefore acronyms) for this time.')

    @property
    def name(self):
        return self.name_at_time()

    @property
    def acronym(self):
        return self.acronym_at_time()

    @property
    def former_name(self):
        name_obj = self.names.all().order_by('start_time')
        if name_obj.count() > 1:
            return list(name_obj)[-2].name
        else:
            return self._name

    @property
    def has_voters(self):
        if self.memberships.filter(role='voter'):
            return True
        else:
            return False
