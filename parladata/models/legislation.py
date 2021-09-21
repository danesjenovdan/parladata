from django.db import models

from tinymce.models import HTMLField

from parladata.behaviors.models import Timestampable, Taggable


class Law(Timestampable, Taggable):
    """Laws which taken place in parlament."""
    STATUSES = [
        ('in_procedure', 'in_procedure'),
        ('enacted', 'enacted'),
        ('submitted', 'submitted'),
        ('rejected', 'rejected'),
        ('adopted', 'adopted'),
        ('received', 'received'),
        ('retracted', 'retracted'),
    ]

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

    status = models.TextField(
        blank=True, null=True,
        choices=STATUSES,
        help_text='Status of law'
    )

    passed = models.BooleanField(blank=True, null=True)

    proposer_text = models.TextField(blank=True, null=True,
                                     help_text='Proposer of law')

    procedure_type = models.TextField(blank=True, null=True,
                                 max_length=255,
                                 help_text='Skrajšani, normalni, hitri postopek...')

    # TODO maybe this can be a choice field
    classification = models.TextField(blank=True, null=True,
                                   help_text='Type of law')

    abstract = HTMLField(blank=True,
                     null=True)

    timestamp = models.DateTimeField(blank=True,
                               null=True,
                               help_text='Date of the law.')

    def __str__(self):
        return (self.session.name if self.session else '') + ' -> ' + self.text

    @property
    def has_votes(self):
        # TODO
        return True

    @property
    def has_abstract(self):
        return bool(self.abstract)
