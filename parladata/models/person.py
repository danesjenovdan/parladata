from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from parladata.behaviors.models import Timestampable


class Person(Timestampable, models.Model):
    """Model for all people that are somehow connected to the parlament."""

    name = models.CharField(_('name'),
                            max_length=128,
                            help_text=_('A person\'s preferred full name'))

    name_parser = models.CharField(max_length=500,
                                   help_text='Name for parser.',
                                   blank=True, null=True)

    classification = models.CharField(_('classification'),
                                      max_length=128,
                                      help_text='Classification for sorting purposes.',
                                      blank=True,
                                      null=True)

    family_name = models.CharField(_('family name'),
                                   max_length=128,
                                   blank=True, null=True,
                                   help_text=_('One or more family names'))

    given_name = models.CharField(_('given name'),
                                  max_length=128,
                                  blank=True, null=True,
                                  help_text=_('One or more primary given names'))

    additional_name = models.CharField(_('additional name'),
                                       max_length=128,
                                       blank=True, null=True,
                                       help_text=_('One or more secondary given names'))

    honorific_prefix = models.CharField(_('honorific prefix'),
                                        max_length=128,
                                        blank=True, null=True,
                                        help_text=_('One or more honorifics preceding a person\'s name'))

    honorific_suffix = models.CharField(_('honorific suffix'),
                                        max_length=128,
                                        blank=True, null=True,
                                        help_text=_('One or more honorifics following a person\'s name'))

    patronymic_name = models.CharField(_('patronymic name'),
                                       max_length=128,
                                       blank=True, null=True,
                                       help_text=_('One or more patronymic names'))

    sort_name = models.CharField(_('sort name'),
                                 max_length=128,
                                 blank=True, null=True,
                                 help_text=_('A name to use in an lexicographically ordered list'))

    previous_occupation = models.TextField(_('previous occupation'),
                                           blank=True, null=True,
                                           help_text=_('The person\'s previous occupation'))

    education = models.TextField(_('education'),
                                 blank=True, null=True,
                                 help_text=_('The person\'s education'))

    education_level = models.TextField(_('education level'),
                                       blank=True, null=True,
                                       help_text=_('The person\'s education level'))

    mandates = models.IntegerField(_('mandates'),
                                   blank=True, null=True,
                                   help_text=_('Person\'s number of mandates, including the current one'))

    email = models.EmailField(_('email'),
                              blank=True, null=True,
                              help_text=_('A preferred email address'))

    gender = models.CharField(_('gender'),
                              max_length=128,
                              blank=True, null=True,
                              help_text=_('A gender'))

    birth_date = models.DateTimeField(_('date of birth'),
                                     blank=True,
                                     null=True,
                                     help_text=_('A date of birth'))

    death_date = models.DateTimeField(_('date of death'),
                                     blank=True,
                                     null=True,
                                     help_text=_('A date of death'))

    summary = models.CharField(_('summary'),
                               max_length=512,
                               blank=True, null=True,
                               help_text=_('A one-line account of a person\'s life'))

    biography = models.TextField(_('biography'),
                                 blank=True, null=True,
                                 help_text=_('An extended account of a person\'s life'))

    image_url = models.URLField(_('image url'),
                            blank=True, null=True,
                            help_text=_('A URL of a head shot from gov site'))

    image = models.ImageField(_('image url'),
                              blank=True,
                              null=True,
                              help_text=_('A image of a head shot'))

    gov_url = models.ForeignKey('Link',
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='URL to gov website profile',
                                related_name='gov_link')

    gov_id = models.CharField(_('gov_id'),
                              max_length=255,
                              blank=True, null=True,
                              help_text='gov website id for the scraper')

    gov_picture_url = models.URLField(_('gov image url'),
                                      blank=True, null=True,
                                      help_text=_('URL to gov website pic'))

    districts = models.ManyToManyField('Area',
                                       blank=True,
                                       help_text='District of person',
                                       related_name="candidates")

    voters = models.IntegerField(_('voters'),
                                 blank=True,
                                 null=True,
                                 help_text='number of votes cast for this person in their district')

    points = models.IntegerField(_('points'),
                                 blank=True,
                                 null=True,
                                 default=None,
                                 help_text='number of points cast for this person')

    active = models.BooleanField(_('active'),
                                 default=True,
                                 help_text='a generic active or not toggle')

    # array of items referencing "http://popoloproject.com/schemas/contact_detail.json"
    def gov_image(self):
        return f'<img src="{self.image_url}" style="width:150px; height: auto;"/>'

    gov_image.allow_tags = True
    url_name = 'person-detail'

    # also handles party and work group memberships
    def add_membership(self, organization):
        m = Membership(person=self, organization=organization)
        m.save()

    def add_memberships(self, organizations):
        for o in organizations:
            self.add_membership(o)

    def add_role(self, post):
        m = Membership(person=self, post=post, organization=post.organization)
        m.save()

    def save(self, *args, **kwargs):
        if self.birth_date:
            self.start_date = self.birth_date
        if self.death_date:
            self.end_date = self.death_date
        super(Person, self).save(*args, **kwargs)

    def __str__(self):
        return self.name + " " + str(self.id)
