# -*- coding: utf-8 -*-

from django.db import models
from model_utils import Choices
from model_utils.managers import PassThroughManager
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import datetime
from .behaviors.models import Timestampable, Taggable, Versionable
from .querysets import PostQuerySet, OtherNameQuerySet, ContactDetailQuerySet, MembershipQuerySet, OrganizationQuerySet, PersonQuerySet
from djgeojson.fields import PolygonField
from django.db.models import Count as dCount


class PopoloDateTimeField(models.DateTimeField):
    """Converting datetime to popolo."""
    def get_popolo_value(self, value):
        return str(datetime.strftime(value, '%Y-%m-%d'))


@python_2_unicode_compatible
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

    birth_date = PopoloDateTimeField(_('date of birth'),
                                     blank=True,
                                     null=True,
                                     help_text=_('A date of birth'))

    death_date = PopoloDateTimeField(_('date of death'),
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

    image = models.URLField(_('image'),
                            blank=True, null=True,
                            help_text=_('A URL of a head shot'))

    gov_url = models.ForeignKey('Link',
                                blank=True, null=True,
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

    active = models.BooleanField(_('active'),
                                 default=True,
                                 help_text='a generic active or not toggle')

    # array of items referencing "http://popoloproject.com/schemas/contact_detail.json"
    def gov_image(self):
        return '<img src="%s" style="width:150px; height: auto;"/>' % self.image

    gov_image.allow_tags = True
    url_name = 'person-detail'
    objects = PassThroughManager.for_queryset_class(PersonQuerySet)()

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
        return self.name + " " + unicode(self.id)


@python_2_unicode_compatible
class Organization(Timestampable, Taggable, models.Model):
    """A group with a common purpose or reason
    for existence that goes beyond the set of people belonging to it.
    """

    _name = models.TextField(_('name'),
                             help_text=_('A primary name, e.g. a legally recognized name'))

    name_parser = models.CharField(max_length=500,
                                   help_text='Name for parser.',
                                   blank=True, null=True)

    # array of items referencing "http://popoloproject.com/schemas/other_name.json#"
    _acronym = models.CharField(_('acronym'),
                                blank=True,
                                null=True,
                                max_length=128,
                                help_text=_('Organization acronym'))

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
                               help_text=_('The organization that contains this organization'))

    dissolution_date = PopoloDateTimeField(blank=True, null=True,
                                           help_text=_('A date of dissolution'))

    founding_date = PopoloDateTimeField(blank=True, null=True,
                                        help_text=_('A date of founding'))

    # array of items referencing "http://popoloproject.com/schemas/contact_detail.json#"
    description = models.TextField(blank=True, null=True,
                                   help_text='Organization description')

    is_coalition = models.IntegerField(blank=True, null=True,
                                       help_text='1 if coalition, -1 if not, 0 if it does not apply')

    url_name = 'organization-detail'

    objects = PassThroughManager.for_queryset_class(OrganizationQuerySet)()

    def __str__(self):
        return self.name + " " + unicode(self.id)

    def name_on(self, fdate=datetime.now()):
        name_obj = self.names.filter(models.Q(start_time__lte=fdate) |
                                     models.Q(start_time=None),
                                     models.Q(end_time__gte=fdate) |
                                     models.Q(end_time=None))
        if name_obj:
            return name_obj[0].name
        else:
            return self._name

    def acronym_on(self, fdate=datetime.now()):
        name_obj = self.names.filter(models.Q(start_time__lte=fdate) |
                                     models.Q(start_time=None),
                                     models.Q(end_time__gte=fdate) |
                                     models.Q(end_time=None))
        if name_obj:
            return name_obj[0].acronym
        else:
            return self._acronym

    @property
    def name(self):
        return self.name_on()

    @property
    def acronym(self):
        return self.acronym_on()

    @property
    def former_name(self):
        name_obj = self.names.all().order_by('start_time')
        if name_obj.count() > 1:
            return list(name_obj)[-2].name
        else:
            return self._name


@python_2_unicode_compatible
class Post(Timestampable, Taggable, models.Model):
    """A position that exists independent of the person holding it."""

    label = models.CharField(_('label'),
                             max_length=128,
                             blank=True, null=True,
                             help_text=_('A label describing the post'))

    role = models.CharField(_('role'),
                            max_length=128,
                            blank=True, null=True,
                            help_text=_('The function that the holder of the post fulfills'))

    # reference to "http://popoloproject.com/schemas/organization.json#"
    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='posts',
                                     help_text=_('The organization in which the post is held'))

    # reference to "http://popoloproject.com/schemas/post.json#"
    membership = models.ForeignKey('Membership',
                                   blank=True, null=True,
                                   related_name='memberships',
                                   help_text=_('The post held by the person in the organization through this membership'))

    # start and end time of memberships
    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')
    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')

    objects = PassThroughManager.for_queryset_class(PostQuerySet)()

    def add_person(self, person):
        m = Membership(post=self, person=person, organization=self.organization)
        m.save()

    def __str__(self):
        return u'Org: {0}, Role: {1}, Person: {2}'.format(self.membership.organization if self.membership else self.organization, self.role, self.membership.person.name if self.membership else "None")


@python_2_unicode_compatible
class Membership(Timestampable, models.Model):
    """A relationship between a person and an organization."""

    label = models.CharField(_('label'),
                             max_length=128,
                             blank=True, null=True,
                             help_text=_('A label describing the membership'))

    role = models.CharField(_('role'),
                            max_length=128,
                            blank=True, null=True,
                            help_text=_('The role that the person fulfills in the organization'))

    # reference to "http://popoloproject.com/schemas/person.json#"
    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               related_name='memberships',
                               help_text=_('The person who is a party to the relationship'))

    # reference to "http://popoloproject.com/schemas/organization.json#"
    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='memberships',
                                     help_text=_('The organization that is a party to the relationship'))

    on_behalf_of = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='memberships_on_behalf_of',
                                     help_text=_('The organization on whose behalf the person is a party to the relationship'))

    # start and end time of memberships
    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')
    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')

    # array of items referencing "http://popoloproject.com/schemas/contact_detail.json#"
    @property
    def slug_source(self):
        return self.label

    objects = PassThroughManager.for_queryset_class(MembershipQuerySet)()

    def __str__(self):
        return u'Person: {0}, Org: {1}, StartTime: {2}'.format(self.person, self.organization, self.start_time.date() if self.start_time else "")


@python_2_unicode_compatible
class ContactDetail(Timestampable, models.Model):
    """A means of contacting an entity."""

    CONTACT_TYPES = Choices(
        ('FAX', 'fax', _('Fax')),
        ('PHONE', 'phone', _('Telephone')),
        ('MOBILE', 'mobile', _('Mobile')),
        ('EMAIL', 'email', _('Email')),
        ('MAIL', 'mail', _('Snail mail')),
        ('TWITTER', 'twitter', _('Twitter')),
        ('FACEBOOK', 'facebook', _('Facebook')),
        ('LINKEDIN', 'linkedin', _('LinkedIn')),
    )

    label = models.CharField(_('label'),
                             max_length=128,
                             blank=True, null=True,
                             help_text=_('A human-readable label for the contact detail'))

    contact_type = models.CharField(_('type'),
                                    max_length=12,
                                    choices=CONTACT_TYPES,
                                    help_text=_('A type of medium, e.g. \'fax\' or \'email\''))

    value = models.CharField(_('value'),
                             max_length=128,
                             help_text=_('A value, e.g. a phone number or email address'))
    note = models.CharField(_('note'),
                            max_length=128,
                            blank=True, null=True,
                            help_text=_('A note, e.g. for grouping contact details by physical location'))

    objects = PassThroughManager.for_queryset_class(ContactDetailQuerySet)()

    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               help_text='The person this name belongs to')
    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     help_text='The organization this name belongs to')

    post = models.ForeignKey('Post',
                             blank=True, null=True,
                             help_text='The person this name belongs to')
    membership = models.ForeignKey('Membership',
                                   blank=True, null=True,
                                   help_text='The organization this name belongs to')

    def __str__(self):
        return u'{0} - {1}'.format(self.value, self.contact_type)


@python_2_unicode_compatible
class OtherName(models.Model):
    """An alternate or former name."""

    name = models.CharField(_('name'),
                            max_length=128,
                            help_text=_('An alternate or former name'))

    note = models.CharField(_('note'),
                            max_length=256,
                            blank=True, null=True,
                            help_text=_('A note, e.g. \'Birth name\''))

    objects = PassThroughManager.for_queryset_class(OtherNameQuerySet)()

    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               help_text='The person this name belongs to')
    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     help_text='The organization this name belongs to')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Identifier(models.Model):
    """An issued identifier."""

    identifier = models.CharField(_('identifier'),
                                  max_length=128,
                                  help_text=_('An issued identifier, e.g. a DUNS number'))

    scheme = models.CharField(_('scheme'),
                              max_length=128,
                              blank=True, null=True,
                              help_text=_('An identifier scheme, e.g. DUNS'))

    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               help_text='The person this identifier belongs to')

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     help_text='The organization this identifier belongs to')

    def __str__(self):
        return '{0}: {1}'.format(self.scheme, self.identifier)


@python_2_unicode_compatible
class Link(Timestampable, Taggable, models.Model):
    """
    A URL
    # max_length increased to account for lengthy Camera's URLS
    """

    url = models.URLField(_('url'),
                          max_length=350,
                          help_text=_('A URL'))

    note = models.CharField(_('note'),
                            max_length=256,
                            blank=True, null=True,
                            help_text=_('A note, e.g. \'Wikipedia page\''),)

    name = models.TextField(blank=True, null=True)

    date = models.DateField(blank=True, null=True)

    session = models.ForeignKey('Session', blank=True, null=True)

    organization = models.ForeignKey('Organization',
                                     blank=True,
                                     null=True,
                                     help_text='The organization of this link.',
                                     related_name='links')

    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               help_text='The person of this link.')

    membership = models.ForeignKey('Membership',
                                   blank=True, null=True,
                                   help_text='The membership of this link.')

    motion = models.ForeignKey('Motion',
                               blank=True,
                               null=True,
                               help_text='The motion of this link.',
                               related_name='links')

    question = models.ForeignKey('Question',
                                 blank=True,
                                 null=True,
                                 help_text='The question this link belongs to.',
                                 related_name='links')

    def __str__(self):
        return self.url


@python_2_unicode_compatible
class Source(Timestampable, Taggable, models.Model):
    """ A URL for referring to sources of information."""

    url = models.URLField(_('url'),
                          help_text=_('A URL'))

    note = models.CharField(_('note'),
                            max_length=256,
                            blank=True, null=True,
                            help_text=_('A note, e.g. \'Parliament website\''))

    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               help_text='The person of this source.')

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     help_text='The organization of this source.')

    post = models.ForeignKey('Post',
                             blank=True, null=True,
                             help_text='The post of this source.')

    membership = models.ForeignKey('Membership',
                                   blank=True, null=True,
                                   help_text='The membership of this source.')

    contact_detail = models.ForeignKey('ContactDetail',
                                       blank=True, null=True,
                                       help_text='The person of this source.')

    def __str__(self):
        return self.url


class Milestone(Taggable, models.Model):
    """Milestone of any kind (beginning, end,...)."""

    year = models.IntegerField(help_text=_('year'),
                               blank=True, null=True)

    month = models.IntegerField(help_text=_('month'),
                                blank=True, null=True)

    day = models.IntegerField(help_text=_('date'),
                              blank=True, null=True)

    hour = models.IntegerField(help_text=_('hour'),
                               blank=True, null=True)

    minute = models.IntegerField(help_text=_('minute'),
                                 blank=True, null=True)

    second = models.IntegerField(help_text=_('second'),
                                 blank=True, null=True)

    kind = models.CharField(max_length=255,
                            blank=True, null=True,
                            help_text='type of milestone')

    start_or_end = models.IntegerField(blank=True, null=True,
                                       help_text='1 for start, -1 for end')

    mandate = models.ForeignKey('Mandate',
                                blank=True, null=True,
                                help_text='The mandate of this milestone.')

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                help_text='The session of this milestone.')

    speech = models.ForeignKey('Speech',
                               blank=True, null=True,
                               help_text='The speech of this milestone.')

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     help_text='The organization of this milestone.')

    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               help_text='The person of this milestone.')


@python_2_unicode_compatible
class Mandate(models.Model):
    """Mandate"""

    description = models.TextField(blank=True,
                                   null=True)

    def __str__(self):
        return self.description


@python_2_unicode_compatible
class Area(Timestampable, Taggable, models.Model):
    """Places of any kind."""

    name = models.CharField(_('name'),
                            max_length=128,
                            help_text=_('Area name'))

    identifier = models.CharField(_('identifier'),
                                  blank=True, null=True,
                                  max_length=128,
                                  help_text='Area identifier')

    parent = models.ForeignKey('Area',
                               blank=True, null=True,
                               help_text='Area parent')

    geometry = PolygonField(blank=True, null=True,
                            help_text='Polygon field for area')

    calssification = models.CharField(_('classification'),
                                      blank=True, null=True,
                                      max_length=128,
                                      help_text='Area classification (Unit/Region)')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Session(Timestampable, Taggable, models.Model):
    """Sessions that happened in parliament."""

    mandate = models.ForeignKey('Mandate',
                                blank=True, null=True,
                                help_text='The mandate of this milestone.')

    name = models.CharField(max_length=255,
                            blank=True, null=True,
                            help_text='Session name')

    gov_id = models.CharField(max_length=255,
                              blank=True, null=True,
                              help_text='Gov website ID.')

    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='session',
                                     help_text='The organization in session')
    organizations = models.ManyToManyField('Organization',
                                           related_name='sessions',
                                           help_text='The organization in session')
    classification = models.CharField(max_length=128,
                                      blank=True, null=True,
                                      help_text='Session classification')

    in_review = models.BooleanField(default=False,
                                    help_text='Is session in review?')

    def __str__(self):
        return unicode(self.name) + ",  " + unicode(self.organization.name)

@python_2_unicode_compatible
class Speech(Versionable, Timestampable, Taggable, models.Model):
    """Speeches that happened in parlament."""

    speaker = models.ForeignKey('Person',
                                help_text='Person making the speech')

    party = models.ForeignKey('Organization',
                              help_text='The party of the person making the speech',
                              default=2)

    content = models.TextField(help_text='Words spoken')

    order = models.IntegerField(blank=True, null=True,
                                help_text='Order of speech')

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                help_text='Speech session')

    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')

    @staticmethod
    def getValidSpeeches(date_):
        return Speech.objects.filter(valid_from__lt=date_, valid_to__gt=date_)

    def __str__(self):
        return self.speaker.name


class Motion(Timestampable, Taggable, models.Model):
    """Votings which taken place in parlament."""
    uid = models.CharField(max_length=64,
                           blank=True, null=True,
                           help_text='motions uid from DZ page')

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     help_text='the organization in which the motion is proposed')

    gov_id = models.CharField(max_length=255,
                              blank=True, null=True,
                              help_text='Government website id')

    date = PopoloDateTimeField(blank=True, null=True,
                               help_text='The date when the motion was proposed')

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                help_text='The legislative session in which the motion was proposed')

    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               help_text='The person who proposed the motion')

    party = models.ForeignKey('Organization',
                              help_text='The party of the person who proposed the motion.',
                              related_name='motion_party',
                              default=2)

    recap = models.TextField(blank=True, null=True,
                             help_text='Motion summary')

    text = models.TextField(blank=True, null=True,
                            help_text='The text of the motion')

    classification = models.CharField(max_length=128,
                                      blank=True, null=True,
                                      help_text='Motion classification')

    requirement = models.CharField(max_length=128,
                                   blank=True, null=True,
                                   help_text='The requirement for the motion to pass')

    result = models.CharField(max_length=128,
                              blank=True, null=True,
                              help_text='Did the motion pass?')

    epa = models.CharField(blank=True, null=True,
                           max_length=255,
                           help_text='EPA number')


class Vote(Timestampable, Taggable, models.Model):
    """Votings which taken place in parlament."""

    name = models.CharField(blank=True, null=True,
                            max_length=1000,
                            help_text='Vote name/identifier')

    motion = models.ForeignKey('Motion',
                               blank=True, null=True,
                               help_text='The motion for which the vote took place')

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     help_text='The organization whose members are voting')

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                help_text='The legislative session in which the vote event occurs')

    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')

    result = models.CharField(blank=True, null=True,
                              max_length=255,
                              help_text='The result of the vote')

    epa = models.CharField(blank=True, null=True,
                           max_length=255,
                           help_text='EPA number')

    epa_url = models.CharField(blank=True, null=True,
                               max_length=515,
                               help_text='gov url for this vote')

    document_url = models.CharField(blank=True, null=True,
                                    max_length=515,
                                    help_text='"document" url for this vote')

    def getResult(self):
        opts = self.ballot_set.all().values_list("option")
        opt_counts = opts.annotate(dCount('option'))

        out = {'ni': 0,
               'proti': 0,
               'za': 0,
               'kvorum': 0
               }
        for opt in opt_counts:
            out[opt[0]] = opt[1]

        return out


class Count(Timestampable, models.Model):
    """Sum of ballots for each option."""

    option = models.CharField(max_length=128,
                              help_text='Yes, no, abstain')

    count = models.IntegerField(help_text='Number of votes')

    vote = models.ForeignKey('Vote',
                             blank=True, null=True,
                             help_text='The vote of this count.')


@python_2_unicode_compatible
class Ballot(Timestampable, models.Model):
    """All ballots from all votes."""

    vote = models.ForeignKey('Vote',
                             help_text='The vote event')

    voter = models.ForeignKey('Person',
                              blank=True, null=True,
                              help_text='The voter')

    voterparty = models.ForeignKey('Organization',
                                   help_text='The party of the voter.',
                                   related_name='party',
                                   default=2)

    orgvoter = models.ForeignKey('Organization',
                                 blank=True,
                                 null=True,
                                 help_text='The voter represents and organisation.')

    option = models.CharField(max_length=128,
                              blank=True, null=True,
                              help_text='Yes, no, abstain')

    def __str__(self):
        return self.voter.name


@python_2_unicode_compatible
class Question(Timestampable, models.Model):
    """All questions from members of parlament."""

    session = models.ForeignKey('Session',
                                blank=True,
                                null=True,
                                help_text='The session this question belongs to.')

    date = PopoloDateTimeField(blank=True,
                               null=True,
                               help_text='Date of the question.')

    title = models.TextField(blank=True,
                             null=True,
                             help_text='Title name as written on dz-rs.si')

    author = models.ForeignKey('Person',
                               blank=True,
                               null=True,
                               help_text='The person (MP) who asked the question.',
                               related_name='asked')
    author_org = models.ForeignKey('Organization',
                                   blank=True,
                                   null=True,
                                   help_text='The organization of person (MP) who asked the question.',
                                   related_name='asked')

    recipient_person = models.ManyToManyField('Person',
                                              blank=True,
                                              help_text='Recipient person (if it\'s a person).',
                                              related_name='questions')

    recipient_post = models.ManyToManyField('Post',
                                            blank=True,
                                            help_text='Recipient person\'s post).',
                                            related_name='questions')

    recipient_organization = models.ManyToManyField('Organization',
                                                    blank=True,
                                                    help_text='Recipient organization (if it\'s an organization).',
                                                    related_name='questions_org')

    recipient_text = models.TextField(blank=True,
                                      null=True,
                                      help_text='Recipient name as written on dz-rs.si')

    json_data = models.TextField(_('json'),
                                 blank=True, null=True,
                                 help_text=_('Debug data'))

    def __str__(self):
        return self.author.name


# Parser "buffer" storage models
@python_2_unicode_compatible
class tmp_votelinks(Timestampable, models.Model):
    session_id = models.CharField(max_length=255,
                                  blank=True,
                                  null=True)

    gov_id = models.CharField(max_length=255,
                              blank=True,
                              null=True)

    votedoc_url = models.CharField(max_length=255,
                                   blank=True,
                                   null=True)

    def __str__(self):
        return self.session_id


@python_2_unicode_compatible
class session_deleted(Timestampable, models.Model):
    mandate_id = models.IntegerField(blank=True,
                                     null=True)

    name = models.CharField(max_length=255,
                            blank=True, null=True,
                            help_text='Session name')

    gov_id = models.CharField(max_length=255,
                              blank=True, null=True,
                              help_text='Gov website ID.')

    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')

    organization_id = models.IntegerField(blank=True,
                                          null=True)

    classification = models.CharField(max_length=128,
                                      blank=True, null=True,
                                      help_text='Session classification')

    in_review = models.BooleanField(default=False,
                                    help_text='Is session in review?')

    def __str__(self):
        return self.name


class Ignore(Timestampable, Taggable, models.Model):
    """
    id's for ignore
    """
    uid = models.CharField(max_length=64,
                           blank=True, null=True,
                           help_text='motions uid from DZ page')


class OrganizationName(Timestampable, models.Model):
    """
    Objects for name history of organization.
    """
    organization = models.ForeignKey('Organization',
                                     help_text=_('The organization who hold this name.'),
                                     related_name='names')

    name = models.TextField(_('name'),
                            help_text=_('A primary name, e.g. a legally recognized name'))

    acronym = models.CharField(_('acronym'),
                               blank=True,
                               null=True,
                               max_length=128,
                               help_text=_('Organization acronym'))

    start_time = PopoloDateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = PopoloDateTimeField(blank=True, null=True,
                                   help_text='End time')


@receiver(pre_save, sender=Organization)
def copy_date_fields(sender, **kwargs):
    obj = kwargs['instance']

    if obj.founding_date:
        obj.start_date = obj.founding_date
    if obj.dissolution_date:
        obj.end_date = obj.dissolution_date


# all instances are validated before being saved
@receiver(pre_save, sender=Person)
@receiver(pre_save, sender=Organization)
@receiver(pre_save, sender=Post)
def validate_date_fields(sender, **kwargs):
    obj = kwargs['instance']
    obj.full_clean()
