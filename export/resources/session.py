from export.resources.common import ExportModelResource
from parladata.models import Vote

from import_export.fields import Field


class VoteResource(ExportModelResource):
    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all votes for given mandate id.
        Or returns all votes if there is no mandate id.
        """
        if mandate_id:
            votes = Vote.objects.filter(
                motion__session__mandate_id=mandate_id,
                motion__session_id=request_id,
            )
            return votes
        else:
            return Vote.objects.all()

    law_id = Field()

    class Meta:
        model = Vote
        fields = ('id', 'name', 'motion__text', 'motion__summary', 'result', 'law_id')
        export_order = ('id', 'name', 'motion__text', 'motion__summary', 'result', 'law_id')

    def dehydrate_law_id(self, vote):
        return vote.motion.law.id if vote.motion.law else None
