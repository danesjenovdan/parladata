from django.db import models
from django.utils.translation import ugettext_lazy as _

from parladata.behaviors.models import Timestampable

class Membership(Timestampable):
    start_time = models.DateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = models.DateTimeField(blank=True, null=True,
                                   help_text='End time')
    
    organization = models.ForeignKey('Organization',
                                     blank=False, null=False,
                                     on_delete=models.CASCADE,
                                     help_text=_('The organization that the member belongs to.'))
    
    def __str__(self):
        return f'Member: {self.member}, Org: {self.organization}, StartTime: {self.start_time}'
    
    class Meta:
        abstract = True

class PersonMembership(Membership):
    """A relationship between a person and an organization."""

    member = models.ForeignKey('Person',
                               blank=False, null=False,
                               on_delete=models.CASCADE,
                               related_name='person_memberships',
                               help_text=_('The person who is a party to the relationship'))

    role = models.TextField(_('role'),
                            blank=False, null=False,
                            default='member',
                            help_text=_('The role that the person fulfills in the organization'))

    on_behalf_of = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     on_delete=models.CASCADE,
                                     related_name='representatives',
                                     help_text=_('The organization on whose behalf the person is a party to the relationship'))


class OrganizationMembership(Membership):
    member = models.ForeignKey('Organization',
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        help_text=_('The organization that is a party to the relationship')
    )
