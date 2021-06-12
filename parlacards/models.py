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


class GroupScore(Score):
    group = models.ForeignKey(
        'parladata.Organization',
        related_name="%(class)s_related",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.group.name}: {self.value}'

    class Meta:
        abstract = True


class PersonVocabularySize(PersonScore):
    pass


class GroupVocabularySize(GroupScore):
    pass


class VotingDistance(PersonScore):
    target = models.ForeignKey(
        'parladata.Person',
        related_name='target_people',
        on_delete=models.CASCADE
    )


class GroupVotingDistance(GroupScore):
    target = models.ForeignKey(
        'parladata.Person',
        related_name='target_organizations',
        on_delete=models.CASCADE
    )


class PersonAvgSpeechesPerSession(PersonScore):
    pass


class DeviationFromGroup(PersonScore):
    pass


class PersonNumberOfQuestions(PersonScore):
    pass


class PersonMonthlyVoteAttendance(PersonScore):
    no_mandate = models.FloatField(blank=False, null=False)


class GroupMonthlyVoteAttendance(GroupScore):
    no_mandate = models.FloatField(blank=False, null=False)


class GroupNumberOfQuestions(GroupScore):
    pass


class PersonVoteAttendance(PersonScore):
    pass


class GroupVoteAttendance(GroupScore):
    pass


class PersonStyleScore(PersonScore):
    style = models.TextField(
        blank=False,
        null=False
    )


class PersonNumberOfSpokenWords(PersonScore):
    pass


class PersonTfidf(PersonScore):
    token = models.TextField(
        blank=False,
        null=False
    )


class GroupTfidf(GroupScore):
    token = models.TextField(
        blank=False,
        null=False
    )
