from django.db import models

from parladata.behaviors.models import Timestampable

class Ballot(Timestampable):
    """All ballots from all votes."""

    vote = models.ForeignKey('Vote',
                             help_text='The vote event',
                             on_delete=models.CASCADE)

    personvoter = models.ForeignKey('Person',
                              blank=True, null=True,
                              on_delete=models.CASCADE,
                              help_text='The voter')

    orgvoter = models.ForeignKey('Organization',
                                 blank=True,
                                 null=True,
                                 on_delete=models.CASCADE,
                                 help_text='The voter represents and organisation.')

    option = models.CharField(max_length=128,
                              blank=True, null=True,
                              help_text='Yes, no, abstain')

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