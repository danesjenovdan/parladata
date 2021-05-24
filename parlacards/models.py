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


class OrganizationScore(Score):
    organization = models.ForeignKey(
        'parladata.Organization',
        related_name='scores',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.organization.name}: {self.value}'

    class Meta:
        abstract = True


class PersonVocabularySize(PersonScore):
    pass


class OrganizationVocabularySize(OrganizationScore):
    pass


class VotingDistance(PersonScore):
    target = models.ForeignKey(
        'parladata.Person',
        related_name='target',
        on_delete=models.CASCADE
    )


class PersonAvgSpeechesPerSession(PersonScore):
    pass


class DeviationFromGroup(PersonScore):
    pass

class PersonNumberOfQuestions(PersonScore):
    pass
