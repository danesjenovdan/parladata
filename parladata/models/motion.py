from django.db import models

from parladata.behaviors.models import Timestampable, Taggable

class Motion(Timestampable, Taggable):
    """Votings which taken place in parlament."""
    # TODO maybe join this with gov_id/epa
    uid = models.TextField(blank=True, null=True,
                           help_text='motions uid from DZ page')

    # TODO maybe join this with uid/epa
    gov_id = models.CharField(max_length=255,
                              blank=True, null=True,
                              help_text='Government website id')

    datetime = models.DateTimeField(blank=True, null=True,
                               help_text='The date and time when the motion was proposed')

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='The legislative session in which the motion was proposed')

    # TODO this should be reworked
    champions = models.ManyToManyField('Person', help_text='The people who proposed the motion.')
    # person = models.ForeignKey('Person',
    #                            blank=True, null=True,
    #                            on_delete=models.CASCADE,
    #                            help_text='The person who proposed the motion')

    # party = models.ForeignKey('Organization',
    #                           help_text='The party of the person who proposed the motion.',
    #                           related_name='motion_party',
    #                           on_delete=models.CASCADE,
    #                           default=2)

    summary = models.TextField(blank=True, null=True,
                             help_text='Motion summary')

    text = models.TextField(blank=True, null=True,
                            help_text='The text of the motion')

    classification = models.TextField(blank=True, null=True,
                                      help_text='Motion classification')

    title = models.TextField(blank=True, null=True,
                             help_text='Title of the motion')

    # TODO rework this into a choice field
    requirement = models.TextField(blank=True, null=True,
                                   help_text='The requirement for the motion to pass')

    # TODO maybe rework this into passed?
    result = models.TextField(blank=True, null=True,
                              help_text='Did the motion pass?')

    # TODO maybe join this with uid/gov_id
    epa = models.CharField(blank=True, null=True,
                           max_length=255,
                           help_text='EPA number')

    agenda_items = models.ManyToManyField('AgendaItem', blank=True,
                                         help_text='Agenda items', related_name='motions')

    # TODO do we need this?
    debate = models.ForeignKey('Debate', blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='Debates', related_name='motions')

    # TODO connect motion to law through FK
    # then we can kill EPA on the motion

    def __str__(self):
        return self.text[:100] + ' --> ' + self.session.name if self.session else ''
