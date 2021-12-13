from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable, Parsable, Sluggable, VersionableFieldsOwner

from parladata.models.memberships import PersonMembership


class Person(Timestampable, Parsable, Sluggable, VersionableFieldsOwner):
    """Model for all people that are somehow connected to the parlament."""

    date_of_birth = models.DateField(_('date of birth'),
                                     blank=True,
                                     null=True,
                                     help_text=_('A date of birth'))

    date_of_death = models.DateField(_('date of death'),
                                     blank=True,
                                     null=True,
                                     help_text=_('A date of death'))

    image = models.ImageField(_('image (url)'),
                              blank=True,
                              null=True,
                              help_text=_('A image of a head shot'))

    districts = models.ManyToManyField('Area',
                                       blank=True,
                                       help_text='District of person',
                                       related_name="candidates")

    # TODO consider this, maybe we don't need it
    active = models.BooleanField(_('active'),
                                 default=True,
                                 help_text='a generic active or not toggle')


    @property
    def name(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='PersonName',
            datetime=datetime.now()
        )

    @property
    def honorific_prefix(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='PersonHonorificPrefix',
            datetime=datetime.now()
        )
    
    @property
    def honorific_suffix(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='PersonHonorificSuffix',
            datetime=datetime.now()
        )
    
    @property
    def preferred_pronoun(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='PersonPreferredPronoun',
            datetime=datetime.now()
        )
    
    @property
    def education(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='PersonEducation',
            datetime=datetime.now()
        )
    
    @property
    def education_level(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='PersonEducationLevel',
            datetime=datetime.now()
        )
    
    @property
    def previous_occupation(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='PersonPreviousOccupation',
            datetime=datetime.now()
        )
    
    @property
    def number_of_mandates(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='PersonNumberOfMandates',
            datetime=datetime.now()
        )
    
    @property
    def number_of_voters(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='PersonNumberOfVoters',
            datetime=datetime.now()
        )
    
    @property
    def email(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name='PersonEmail',
            datetime=datetime.now()
        )

    def parliamentary_group_on_date(self, timestamp=datetime.now()):
        active_memberships = PersonMembership.objects.filter(
            models.Q(member=self),
            models.Q(start_time__lte=timestamp) | models.Q(start_time__isnull=True),
            models.Q(end_time__gte=timestamp) | models.Q(end_time__isnull=True),
            models.Q(organization__classification='pg'), # TODO change to parliamentary_group
        )

        if active_memberships.count() > 1:
            # TODO we need a way to bubble these
            # exceptions up to the end user
            raise Exception('\n'.join(
                [
                    f'{active_memberships.count()} active memberships for person {self.id}. Check your data.',
                    f'Membership ids: {list(active_memberships.values_list("id", flat=True))}'
                ]
            ))
        
        active_membership = active_memberships.first()

        if not active_membership:
            return None

        return active_membership.organization

    def __str__(self):
        return f'{self.id}: {self.name}'

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'People'
