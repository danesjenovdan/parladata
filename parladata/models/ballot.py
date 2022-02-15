from django.db import models
from django.core.exceptions import ValidationError

from parladata.behaviors.models import Timestampable


class Ballot(Timestampable):
    """All ballots from all votes."""
    OPTIONS = [
        ('for', 'for'),
        ('against', 'against'),
        ('abstain', 'abstain'),
        ('absent', 'absent'),

        # following is a special case for slovenian
        # municipalities there are situations where
        # they check if they have a majority of yeses
        # and if they do they don't ask anyone else
        # if they are against or abstained
        ('did not vote', 'did not vote'),
    ]

    vote = models.ForeignKey('Vote',
                             help_text='The vote event',
                             related_name='ballots',
                             on_delete=models.CASCADE)

    personvoter = models.ForeignKey('Person',
                              blank=True, null=True,
                              on_delete=models.CASCADE,
                              related_name='ballots',
                              help_text='The voter')

    orgvoter = models.ForeignKey('Organization',
                                 blank=True,
                                 null=True,
                                 on_delete=models.CASCADE,
                                 help_text='The voter represents and organisation.')

    option = models.CharField(max_length=128,
                              blank=True, null=True,
                              help_text='Yes, no, abstain',
                              choices=OPTIONS)

    @property
    def voter(self):
        if self.personvoter and self.orgvoter:
            raise Exception(f'Both personvoter and orgvoter are set for this ballot (id {self.id}). Something is wrong.')

        if self.personvoter:
            return self.personvoter

        if self.orgvoter:
            return self.orgvoter

        raise Exception('No voter is set (neither personvoter or orgvoter).')

    def __str__(self):
        return self.voter.name

    def clean(self):
        if self.personvoter and self.orgvoter:
            raise ValidationError("The ballot should have only one of personvoter or orgvoter filled field.")
