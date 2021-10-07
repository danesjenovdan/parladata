from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from parladata.behaviors.models import Timestampable


# TODO touch parents on save
# TODO touch parents on delete

class ActiveAtQuerySet(models.QuerySet):
    def active_at(self, timestamp):
        return self.filter(
            models.Q(start_time__lte=timestamp) | models.Q(start_time__isnull=True),
            models.Q(end_time__gte=timestamp) | models.Q(end_time__isnull=True)
        )

class Membership(Timestampable):
    start_time = models.DateTimeField(
        blank=True, null=True,
        help_text='Start time'
    )

    end_time = models.DateTimeField(
        blank=True, null=True,
        help_text='End time'
    )

    organization = models.ForeignKey(
        'Organization',
        blank=False, null=False,
        related_name="%(class)ss_children",
        on_delete=models.CASCADE,
        help_text=_('The organization that the member belongs to.')
    )

    mandate = models.ForeignKey(
        'Mandate',
        blank=True, null=True,
        verbose_name=_("Mandate"),
        related_name="%(class)ss",
        on_delete=models.CASCADE
    )

    objects = ActiveAtQuerySet.as_manager()

    def __str__(self):
        return f'Member: {self.member}, Org: {self.organization}, StartTime: {self.start_time}'

    class Meta:
        abstract = True

class PersonMembership(Membership):
    """A relationship between a person and an organization."""
    ROLES = [
        ('member', 'member'),
        ('voter', 'voter'),
        ('president', 'president'),
        ('deputy', 'deputy'),
    ]

    member = models.ForeignKey('Person',
                               blank=False, null=False,
                               on_delete=models.CASCADE,
                               related_name='person_memberships',
                               help_text=_('The person who is a party to the relationship'))

    role = models.TextField(_('role'),
                            blank=False, null=False,
                            default='member',
                            choices=ROLES,
                            help_text=_('The role that the person fulfills in the organization'))

    on_behalf_of = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     on_delete=models.CASCADE,
                                     related_name='representatives',
                                     help_text=_('The organization on whose behalf the person is a party to the relationship'))

    def __str__(self):
        return f'{self.role}: {self.member}, Org: {self.organization}, StartTime: {self.start_time}'

    @staticmethod
    def valid_at(timestamp):
        return PersonMembership.objects.filter(
            models.Q(start_time__lte=timestamp) | models.Q(start_time__isnull=True),
            models.Q(end_time__gte=timestamp) | models.Q(end_time__isnull=True),
        )

    @staticmethod
    def valid_before(timestamp):
        return PersonMembership.objects.filter(
            models.Q(start_time__lte=timestamp) | models.Q(start_time__isnull=True)
        )


class OrganizationMembership(Membership):
    member = models.ForeignKey('Organization',
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        help_text=_('The organization that is a party to the relationship')
    )

    @staticmethod
    def valid_at(date=datetime.now()):
        return OrganizationMembership.objects.filter(
            models.Q(start_time__lte=date) | models.Q(start_time__isnull=True),
            models.Q(end_time__gte=date) | models.Q(end_time__isnull=True),
        )
