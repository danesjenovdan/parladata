from django.db import models

from tinymce.models import HTMLField

from parladata.behaviors.models import Timestampable, Taggable

class Law(Timestampable, Taggable):
    """Laws which taken place in parlament."""

    uid = models.TextField(blank=True, null=True,
                           help_text='law uid from DZ page')


    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='The legislative session in which the law was proposed')


    text = models.TextField(blank=True, null=True,
                            help_text='The text of the law')


    epa = models.TextField(blank=True, null=True,
                           help_text='EPA number')

    mdt = models.TextField(blank=True, null=True,
                           max_length=1024,
                           help_text='Working body text')

    mdt_fk = models.ForeignKey('Organization',
                               related_name='laws',
                               blank=True, null=True,
                               max_length=255,
                               on_delete=models.CASCADE,
                               help_text='Working body obj')

    # TODO this is weird, compare with result
    status = models.CharField(blank=True, null=True,
                             max_length=255,
                             help_text='result of law')

    # TODO this is weird, compare with status
    result = models.CharField(blank=True, null=True,
                              max_length=255,
                              help_text='result of law')

    proposer_text = models.TextField(blank=True, null=True,
                                     help_text='Proposer of law')

    # TODO this is weird, compare with procedure
    procedure_phase = models.CharField(blank=True, null=True,
                                       max_length=255,
                                       help_text='Procedure phase of law')

    # TODO this is weird, compare with procedure_phase
    procedure = models.CharField(blank=True, null=True,
                                 max_length=255,
                                 help_text='Procedure of law')

    # TODO is this necessary, if we have tags? maybe we don't need tags
    type_of_law = models.CharField(blank=True, null=True,
                                   max_length=255,
                                   help_text='Type of law')

    abstract = HTMLField(blank=True,
                     null=True)

    datetime = models.DateTimeField(blank=True,
                               null=True,
                               help_text='Date of the law.')

    classification = models.TextField(blank=True, null=True,
                                      help_text='Type of law')

    # TODO maybe transform into a functional property
    procedure_ended = models.BooleanField(default=False,
                                          max_length=255,
                                          help_text='Procedure phase of law')

    def __str__(self):
        return (self.session.name if self.session else '') + ' -> ' + self.text
