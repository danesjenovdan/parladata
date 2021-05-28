from django.db import models

from parladata.behaviors.models import Versionable, Timestampable

from parlacards.scores.common import tokenize, remove_punctuation, lemmatize_many

class ValidSpeechesManager(models.Manager):
    def filter_valid_speeches(self, date_):
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

    lemmatized_content = models.TextField(blank=True, null=True, help_text='Lemmatized words spoken')

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

    objects = ValidSpeechesManager()

    def __str__(self):
        return f'{self.speaker.name} @ {self.session.name}:{self.order}'
    
    def lemmatize_self(self):
        if self.lemmatized_content:
            return
        
        self.lemmatized_content = ' '.join(
            [lemmatized_token for lemmatized_token in lemmatize_many(
                tokenize(
                    remove_punctuation(
                        self.content.strip().lower()
                    )
                )
            )]
        )
        self.save()

    @property
    def agenda_item(self):
        if self.agenda_items.all().count() > 1:
            raise Exception('This session belongs to multiple agenda items. Use the plural form "agenda_items".')
        
        return self.agenda_items.first()

    @property
    def parliamentary_group(self):
        return self.speaker.parliamentary_group_on_date(datetime=self.start_time)