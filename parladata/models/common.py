from datetime import datetime
from django.db import models
from django.db.models import Q

from parladata.behaviors.models import Timestampable
from parladata.models.memberships import OrganizationMembership


class ActiveAtQuerySet(models.QuerySet):
    def active_at(self, timestamp):
        return self.filter(
            Q(beginning__lte=timestamp) | Q(beginning__isnull=True),
            Q(ending__gte=timestamp) | Q(ending__isnull=True)
        )


class Mandate(models.Model):
    """Mandate"""

    description = models.TextField(blank=True, null=True)

    beginning = models.DateTimeField(blank=True, null=True)

    ending = models.DateTimeField(blank=True, null=True)

    objects = ActiveAtQuerySet.as_manager()

    def query_root_organizations(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        try:
            membership = OrganizationMembership.valid_at(timestamp).get(mandate=self)
        except OrganizationMembership.DoesNotExist:
            raise Exception(f'No root organization memberships exist for this mandate!')
        except OrganizationMembership.MultipleObjectsReturned:
            raise Exception(f'Multiple root organization memberships exist for this mandate!')

        playing_field = membership.member
        root_organization = membership.organization

        return root_organization, playing_field

    def __str__(self):
        return self.description

    def get_time_range_from_mandate(self, to_timestamp):
        if self.beginning:
            from_timestamp = self.beginning
        else:
            from_timestamp = datetime.min

        if self.ending and self.ending < to_timestamp:
            to_timestamp = self.ending
        else:
            to_timestamp = to_timestamp

        return from_timestamp, to_timestamp

    @classmethod
    def get_active_mandate_at(cls, timestamp):
        mandate = Mandate.objects.active_at(timestamp).first()
        if mandate:
            return mandate
        else:
            raise Exception('There\'s no mandate for the given timestamp')


class EducationLevel(Timestampable):
    text = models.TextField()
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text

    class Meta(object):
        ordering = ['order']
