from datetime import datetime
from django.db import models
from parladata.behaviors.models import Timestampable
from parladata.models.memberships import OrganizationMembership

# TODO razmisli kako bomo to uredili
# želimo imeti možnost, da je v eni bazi
# več sklicev
class Mandate(models.Model):
    """Mandate"""

    description = models.TextField(blank=True, null=True)

    beginning = models.DateTimeField(blank=True, null=True)

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


class EducationLevel(Timestampable):
    text = models.TextField()
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text

    class Meta(object):
        ordering = ['order']
