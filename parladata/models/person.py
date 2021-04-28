from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from parladata.behaviors.models import Timestampable, Parsable


class Person(Timestampable, Parsable):
    """Model for all people that are somehow connected to the parlament."""

    # MAYBE make name change-able like
    # in organization with OrganizationName
    name = models.CharField(_('name'),
                            max_length=128,
                            help_text=_('A person\'s preferred full name'))

    honorific_prefix = models.CharField(_('honorific prefix'),
                                        max_length=128,
                                        blank=True, null=True,
                                        help_text=_('One or more honorifics preceding a person\'s name'))

    honorific_suffix = models.CharField(_('honorific suffix'),
                                        max_length=128,
                                        blank=True, null=True,
                                        help_text=_('One or more honorifics following a person\'s name'))

    previous_occupation = models.TextField(_('previous occupation'),
                                           blank=True, null=True,
                                           help_text=_('The person\'s previous occupation'))

    education = models.TextField(_('education'),
                                 blank=True, null=True,
                                 help_text=_('The person\'s education. Their "topic", like "computer science".'))

    education_level = models.TextField(_('education level'),
                                       blank=True, null=True,
                                       help_text=_('The person\'s education level (what they would use to determine their pay in the public sector).'))

    number_of_mandates = models.IntegerField(_('number of mandates'),
                                   blank=True, null=True,
                                   help_text=_('Person\'s number of mandates, including the current one'))

    email = models.EmailField(_('email'),
                              blank=True, null=True,
                              help_text=_('Official (office) email'))

    # TODO make this a selection
    # he
    # she
    # they
    preferred_pronoun = models.CharField(_('preferred pronoun'),
                              max_length=128,
                              blank=True, null=True,
                              help_text=_('Persons preferred pronoun'))

    date_of_birth = models.DateTimeField(_('date of birth'),
                                     blank=True,
                                     null=True,
                                     help_text=_('A date of birth'))

    date_of_death = models.DateTimeField(_('date of death'),
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

    number_of_voters = models.IntegerField(_('number of voters'),
                                 blank=True,
                                 null=True,
                                 help_text='number of votes cast for this person in their district(s)')

    number_of_points = models.IntegerField(_('number of points awarded'),
                                 blank=True,
                                 null=True,
                                 default=None,
                                 help_text='number of points cast for this person (in a point-based voting system)')

    # TODO consider this, maybe we don't need it
    active = models.BooleanField(_('active'),
                                 default=True,
                                 help_text='a generic active or not toggle')

    def __str__(self):
        return f'{self.id}: {self.name}'

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'People'
