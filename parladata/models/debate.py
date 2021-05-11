from django.db import models

from parladata.behaviors.models import Timestampable, Taggable

class Debate(Timestampable, Taggable):
    order = models.IntegerField(blank=True, null=True,
                                help_text='Order of debate')

    datetime = models.DateTimeField(blank=True,
                               null=True,
                               help_text='Date of the item.')

    agenda_items = models.ManyToManyField('AgendaItem', blank=True,
                                         help_text='Agenda item', related_name='debates')

    gov_id = models.TextField(blank=True, null=True, help_text='gov_id of debate')

    session = models.ForeignKey('Session', blank=True, null=True, on_delete=models.CASCADE)
