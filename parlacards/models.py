from django.db import models

from parladata.behaviors.models import Timestampable

# Create your models here.
class Score(Timestampable):
    timestamp = models.DateTimeField(blank=False, null=False)
    value = models.FloatField(blank=False, null=False)
    playing_field = models.ForeignKey(
        'parladata.Organization',
        on_delete=models.CASCADE,
    )
    # TODO maybe add mandate?

    class Meta:
        abstract = True


class PersonScore(Score):
    person = models.ForeignKey(
        'parladata.Person',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.person.name}: {self.value}'

    class Meta:
        abstract = True


class PersonVocabularySize(PersonScore):
    pass
