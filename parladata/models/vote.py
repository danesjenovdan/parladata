from django.db import models

from parladata.behaviors.models import Timestampable, Taggable

class Vote(Timestampable, Taggable):
    """Votings which taken place in parlament."""

    name = models.TextField(
        blank=True,
        null=True,
        help_text='Vote name/identifier'
    )

    motion = models.ForeignKey(
        'Motion',
        blank=True, null=True,
        related_name='vote',
        on_delete=models.CASCADE,
        help_text='The motion for which the vote took place'
    )

    timestamp = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Vote time'
    )

    needs_editing = models.BooleanField(
        "Is vote needs editing",
        default=False
    )

    result = models.BooleanField(
        blank=True,
        null=True,
        help_text='The result of the vote'
    )

    def get_option_counts(self):
        annotated_ballots = self.ballots.all().values(
            'option'
        ).annotate(
            option_count=models.Count('option')
        ).order_by('-option_count')

        option_counts = {
            option_sum['option']: option_sum['option_count'] for
            option_sum in annotated_ballots
        }

        # we need this to also show zeroes
        return {
            key: option_counts.get(key, 0) for
            key in ['absent', 'abstain', 'for', 'against'] # TODO get this from global var
        }

    def __str__(self):
        return self.name
