# -*- coding: utf-8 -*-

from django.db import models
from model_utils import Choices
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from parladata.behaviors.models import Timestampable, Taggable, Versionable
from django.db.models import Count as dCount
from tinymce.models import HTMLField
from parladata.models.organization import Organization


class PersonMembership(Timestampable, models.Model):
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
                               on_delete=models.CASCADE,
                               help_text=_('The person who is a party to the relationship'))

    # reference to "http://popoloproject.com/schemas/organization.json#"
    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='memberships',
                                     on_delete=models.CASCADE,
                                     help_text=_('The organization that is a party to the relationship'))

    on_behalf_of = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='memberships_on_behalf_of',
                                     on_delete=models.CASCADE,
                                     help_text=_('The organization on whose behalf the person is a party to the relationship'))

    # start and end time of memberships
    start_time = models.DateTimeField(blank=True, null=True,
                                     help_text='Start time')
    end_time = models.DateTimeField(blank=True, null=True,
                                   help_text='End time')

    # array of items referencing "http://popoloproject.com/schemas/contact_detail.json#"
    @property
    def slug_source(self):
        return self.label

    def __str__(self):
        return u'Person: {0}, Org: {1}, StartTime: {2}'.format(self.person, self.organization, self.start_time.date() if self.start_time else "")


class OrganizationMembership(Timestampable, models.Model):
    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='organization_memberships',
                                     on_delete=models.CASCADE,
                                     help_text=_('The organization that is a party to the relationship'))

    parent = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='organization_parent_memberships',
                                     on_delete=models.CASCADE,
                                     help_text=_('The organization which is parent in the relationship'))

    start_time = models.DateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = models.DateTimeField(blank=True, null=True,
                                   help_text='End time')


# TODO think about this
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

    session = models.ForeignKey('Session', blank=True, null=True, on_delete=models.CASCADE)

    organization = models.ForeignKey('Organization',
                                     blank=True,
                                     null=True,
                                     on_delete=models.CASCADE,
                                     help_text='The organization of this link.',
                                     related_name='links')

    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               on_delete=models.CASCADE,
                               help_text='The person of this link.')

    membership = models.ForeignKey('PersonMembership',
                                   blank=True, null=True,
                                   on_delete=models.CASCADE,
                                   help_text='The membership of this link.')

    motion = models.ForeignKey('Motion',
                               blank=True,
                               null=True,
                               on_delete=models.CASCADE,
                               help_text='The motion of this link.',
                               related_name='links')

    question = models.ForeignKey('Question',
                                 blank=True,
                                 null=True,
                                 on_delete=models.CASCADE,
                                 help_text='The question this link belongs to.',
                                 related_name='links')

    def __str__(self):
        return self.url


# TODO razmisli kako bomo to uredili
# želimo imeti možnost, da je v eni bazi
# več sklicev
class Mandate(models.Model):
    """Mandate"""

    description = models.TextField(blank=True,
                                   null=True)

    def __str__(self):
        return self.description


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
                               on_delete=models.CASCADE,
                               help_text='Area parent')

    #geometry = gis_models.PolygonField(blank=True, null=True,
    #                        help_text='Polygon field for area')

    calssification = models.CharField(_('classification'),
                                      blank=True, null=True,
                                      max_length=128,
                                      help_text='Area classification (Unit/Region)')

    def __str__(self):
        return self.name


class Session(Timestampable, Taggable, models.Model):
    """Sessions that happened in parliament."""

    mandate = models.ForeignKey('Mandate',
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='The mandate of this milestone.')

    name = models.CharField(max_length=255,
                            blank=True, null=True,
                            help_text='Session name')

    gov_id = models.CharField(max_length=255,
                              blank=True, null=True,
                              help_text='Gov website ID.')

    start_time = models.DateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = models.DateTimeField(blank=True, null=True,
                                   help_text='End time')

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     related_name='session',
                                     on_delete=models.CASCADE,
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
        if self and self.organization:
          return str(self.name) + ",  " + str(self.organization.name)
        else:
          return "Session"


class SpeechQuerySet(models.QuerySet):
    def getValidSpeeches(self, date_):
        return Speech.objects.filter(valid_from__lt=date_, valid_to__gt=date_)


class Speech(Versionable, Timestampable, Taggable, models.Model):
    """Speeches that happened in parlament."""

    speaker = models.ForeignKey('Person',
                                on_delete=models.CASCADE,
                                help_text='Person making the speech')

    party = models.ForeignKey('Organization', null=True, blank=True,
                              on_delete=models.CASCADE,
                              help_text='The party of the person making the speech',
                              default=2)

    content = models.TextField(help_text='Words spoken')

    order = models.IntegerField(blank=True, null=True,
                                help_text='Order of speech')

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='Speech session')

    start_time = models.DateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = models.DateTimeField(blank=True, null=True,
                                   help_text='End time')

    version_con = models.IntegerField(blank=True, null=True,
                                      help_text='Order of speech')

    agenda_item = models.ForeignKey('AgendaItem', blank=True, null=True,
                                    on_delete=models.CASCADE,
                                    help_text='Agenda item', related_name='speeches')

    agenda_items = models.ManyToManyField('AgendaItem', blank=True,
                                          help_text='Agenda items', related_name='speeches_many')

    debate = models.ForeignKey('Debate', blank=True, null=True,
                                help_text='Debates', related_name='speeches',
                                on_delete=models.CASCADE,)

    objects = models.Manager.from_queryset(SpeechQuerySet)()

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
                                     on_delete=models.CASCADE,
                                     help_text='the organization in which the motion is proposed')

    gov_id = models.CharField(max_length=255,
                              blank=True, null=True,
                              help_text='Government website id')

    date = models.DateTimeField(blank=True, null=True,
                               help_text='The date when the motion was proposed')

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='The legislative session in which the motion was proposed')

    person = models.ForeignKey('Person',
                               blank=True, null=True,
                               on_delete=models.CASCADE,
                               help_text='The person who proposed the motion')

    party = models.ForeignKey('Organization',
                              help_text='The party of the person who proposed the motion.',
                              related_name='motion_party',
                              on_delete=models.CASCADE,
                              default=2)

    recap = models.TextField(blank=True, null=True,
                             help_text='Motion summary')

    text = models.TextField(blank=True, null=True,
                            help_text='The text of the motion')

    classification = models.CharField(max_length=128,
                                      blank=True, null=True,
                                      help_text='Motion classification')

    title = models.TextField(blank=True, null=True,
                             help_text='Title motion')

    doc_title = models.TextField(blank=True, null=True,
                                 help_text='Title of document')

    requirement = models.CharField(max_length=128,
                                   blank=True, null=True,
                                   help_text='The requirement for the motion to pass')

    result = models.CharField(max_length=128,
                              blank=True, null=True,
                              help_text='Did the motion pass?')

    epa = models.CharField(blank=True, null=True,
                           max_length=255,
                           help_text='EPA number')

    agenda_item = models.ManyToManyField('AgendaItem', blank=True,
                                         help_text='Agenda item', related_name='motions')

    debate = models.ForeignKey('Debate', blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='Debates', related_name='motions')

    def __str__(self):
        return self.text[:100] + ' --> ' + self.session.name if self.session else ''


class Vote(Timestampable, Taggable, models.Model):
    """Votings which taken place in parlament."""

    name = models.CharField(blank=True, null=True,
                            max_length=1000,
                            help_text='Vote name/identifier')

    motion = models.ForeignKey('Motion',
                               blank=True, null=True,
                               related_name='vote',
                               on_delete=models.CASCADE,
                               help_text='The motion for which the vote took place')

    organization = models.ForeignKey('Organization',
                                     blank=True, null=True,
                                     on_delete=models.CASCADE,
                                     help_text='The organization whose members are voting')

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='The legislative session in which the vote event occurs')

    start_time = models.DateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = models.DateTimeField(blank=True, null=True,
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

    counter = models.TextField(_('json'),
                               blank=True, null=True,
                               help_text=_('Counter of ballot option'))
    def getResult(self):
        opts = self.ballot_set.all().values_list("option")
        opt_counts = opts.annotate(dCount('option'))

        out = {'for': 0,
               'against': 0,
               'abstain': 0,
               'absent': 0
               }
        for opt in opt_counts:
            out[opt[0]] = opt[1]
        if not opts:
            out = self.counter
        return out


class Count(Timestampable, models.Model):
    """Sum of ballots for each option."""

    option = models.CharField(max_length=128,
                              help_text='Yes, no, abstain')

    count = models.IntegerField(help_text='Number of votes')

    vote = models.ForeignKey('Vote',
                             blank=True, null=True,
                             on_delete=models.CASCADE,
                             help_text='The vote of this count.')


class Ballot(Timestampable, models.Model):
    """All ballots from all votes."""

    vote = models.ForeignKey('Vote',
                             help_text='The vote event',
                             on_delete=models.CASCADE)

    voter = models.ForeignKey('Person',
                              blank=True, null=True,
                              on_delete=models.CASCADE,
                              help_text='The voter')

    voterparty = models.ForeignKey('Organization',
                                   help_text='The party of the voter.',
                                   related_name='party',
                                   on_delete=models.CASCADE,
                                   default=2)

    orgvoter = models.ForeignKey('Organization',
                                 blank=True,
                                 null=True,
                                 on_delete=models.CASCADE,
                                 help_text='The voter represents and organisation.')

    option = models.CharField(max_length=128,
                              blank=True, null=True,
                              help_text='Yes, no, abstain')

    def __str__(self):
        return self.voter.name


class Question(Timestampable, models.Model):
    """All questions from members of parlament."""

    session = models.ForeignKey('Session',
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE,
                                help_text='The session this question belongs to.')

    date = models.DateTimeField(blank=True,
                               null=True,
                               help_text='Date of the question.')

    date_of_answer = models.DateTimeField(blank=True,
                                         null=True,
                                         help_text='Date of answer the question.')

    title = models.TextField(blank=True,
                             null=True,
                             help_text='Title name as written on dz-rs.si')

    authors = models.ManyToManyField('Person',
                                     blank=True,
                                     help_text='The persons (MP) who asked the question.')

    author_orgs = models.ManyToManyField('Organization',
                                         blank=True,
                                         help_text='The organizations of person (MP) who asked the question.')

    recipient_person = models.ManyToManyField('Person',
                                              blank=True,
                                              help_text='Recipient person (if it\'s a person).',
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

    signature = models.TextField(_('Unique signature'),
                                 blank=True, null=True,
                                 help_text=_('Unique signature'))

    type_of_question = models.CharField(max_length=64,
                                   blank=True,
                                   null=True)

    def __str__(self):
        return ' '.join(self.authors.all().values_list('name', flat=True))


class Law(Timestampable, Taggable, models.Model):
    """Laws which taken place in parlament."""

    uid = models.CharField(max_length=64,
                           blank=True, null=True,
                           help_text='law uid from DZ page')


    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='The legislative session in which the law was proposed')


    text = models.TextField(blank=True, null=True,
                            help_text='The text of the law')


    epa = models.CharField(blank=True, null=True,
                           max_length=255,
                           help_text='EPA number')

    mdt = models.CharField(blank=True, null=True,
                           max_length=1024,
                           help_text='Working body text')

    mdt_fk = models.ForeignKey('Organization',
                               related_name='laws',
                               blank=True, null=True,
                               max_length=255,
                               on_delete=models.CASCADE,
                               help_text='Working body obj')

    status = models.CharField(blank=True, null=True,
                             max_length=255,
                             help_text='result of law')

    result = models.CharField(blank=True, null=True,
                              max_length=255,
                              help_text='result of law')

    proposer_text = models.TextField(blank=True, null=True,
                                     help_text='Proposer of law')

    procedure_phase = models.CharField(blank=True, null=True,
                                       max_length=255,
                                       help_text='Procedure phase of law')

    procedure = models.CharField(blank=True, null=True,
                                 max_length=255,
                                 help_text='Procedure of law')

    type_of_law = models.CharField(blank=True, null=True,
                                   max_length=255,
                                   help_text='Type of law')

    note = HTMLField(blank=True,
                     null=True)

    date = models.DateTimeField(blank=True,
                               null=True,
                               help_text='Date of the law.')

    classification = models.CharField(blank=True, null=True,
                                      max_length=255,
                                      help_text='Type of law')

    procedure_ended = models.BooleanField(default=False,
                                          max_length=255,
                                          help_text='Procedure phase of law')

    def __str__(self):
        return (self.session.name if self.session else '') + ' -> ' + self.text


class AgendaItem(Timestampable, Taggable, models.Model):
    name = models.TextField(blank=True, null=True,
                            help_text='The name of agenda')

    date = models.DateTimeField(blank=True,
                               null=True,
                               help_text='Date of the item.')

    session = models.ForeignKey('Session', blank=True, null=True,
                                on_delete=models.CASCADE,)

    order = models.IntegerField(blank=True, null=True,
                                help_text='Order of agenda item')

    gov_id = models.CharField(blank=True, max_length=255, null=True, help_text='gov_id of agenda item')

    def __str__(self):
        return (self.session.name if self.session else '') + ' -> ' + self.name


class Debate(Timestampable, Taggable, models.Model):
    order = models.IntegerField(blank=True, null=True,
                                help_text='Order of debate')

    date = models.DateTimeField(blank=True,
                               null=True,
                               help_text='Date of the item.')

    agenda_item = models.ManyToManyField('AgendaItem', blank=True,
                                         help_text='Agenda item', related_name='debates')

    gov_id = models.CharField(blank=True, max_length=255, null=True, help_text='gov_id of debate')

    session = models.ForeignKey('Session', blank=True, null=True, on_delete=models.CASCADE,)

