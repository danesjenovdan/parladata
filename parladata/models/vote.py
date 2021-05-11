from django.db import models

from parladata.behaviors.models import Timestampable, Taggable

class Vote(Timestampable, Taggable):
    """Votings which taken place in parlament."""

    name = models.TextField(blank=True, null=True,
                            help_text='Vote name/identifier')

    motion = models.ForeignKey('Motion',
                               blank=True, null=True,
                               related_name='vote',
                               on_delete=models.CASCADE,
                               help_text='The motion for which the vote took place')

    datetime = models.DateTimeField(blank=True, null=True,
                                     help_text='Vote time')

    # TODO maybe rework this into a choice field
    result = models.TextField(blank=True, null=True,
                              help_text='The result of the vote')

    def getBallotCounts(self):
        opts = self.ballot_set.all().values_list("option")
        if not opts:
            return None

        opt_counts = opts.annotate(models.Count('option'))

        out = {'for': 0,
               'against': 0,
               'abstain': 0,
               'absent': 0
               }
        for opt in opt_counts:
            out[opt[0]] = opt[1]

        return out
