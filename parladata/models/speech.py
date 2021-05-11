from django.db import models

from parladata.behaviors.models import Versionable, Timestampable

class ValidSpeechesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            models.Q(valid_from__lt=date_) | models.Q(valid_from__isnull=True),
            models.Q(valid_to__gt=date_) | models.Q(valid_to__isnull=True)
        )


class Speech(Versionable, Timestampable):
    """Speeches that happened in parlament."""

    speaker = models.ForeignKey('Person',
                                on_delete=models.CASCADE,
                                help_text='Person making the speech')

    content = models.TextField(blank=False, null=False, help_text='Words spoken')

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

    agenda_items = models.ManyToManyField('AgendaItem', blank=True,
                                          help_text='Agenda items', related_name='speeches')

    debate = models.ForeignKey('Debate', blank=True, null=True,
                                help_text='Debates', related_name='speeches',
                                on_delete=models.CASCADE,)

    objects = models.Manager()
    valid_speeches = ValidSpeechesManager()

    def __str__(self):
        return f'{self.speaker.name} @ {self.session.name}:{self.order}'

    @property
    def agenda_item(self):
        if self.agenda_items.all().count() > 1:
            raise Exception('This session belongs to multiple agenda items. Use the plural form "agenda_items".')
        
        return self.agenda_items.first()

    # TODO rename to parliamentary_group
    @property
    def party(self):
        return self.speaker.parliamentary_group_on_date(datetime=self.start_time)
