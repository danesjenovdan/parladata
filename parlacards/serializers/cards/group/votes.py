from django.db.models import Max

from parladata.models.vote import Vote
from parladata.models.ballot import Ballot
from parladata.models.memberships import PersonMembership

from parlacards.serializers.common import GroupScoreCardSerializer
from parlacards.serializers.vote import VoteSerializer
from parlacards.serializers.ballot import BallotSerializer

from parlacards.pagination import create_paginator

class GroupVoteCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the group
        votes = Vote.objects.filter(
            timestamp__lte=self.context['date']
        ).order_by(
            '-timestamp',
            '-id' # fallback ordering
        )

        # TODO: maybe lemmatize?, maybe search by each word separately?
        if text := self.context.get('GET', {}).get('text', None):
            votes = votes.filter(motion__text__icontains=text)

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), votes)

        party_ballots = []
        for vote in paged_object_list:
            voter_ids = PersonMembership.valid_at(vote.timestamp).filter(
                # instance is the group
                on_behalf_of=instance,
                role='voter'
            ).values_list('member_id', flat=True)

            # TODO this is very similar to
            # parlacards.scores.devaition_from_group.get_group_ballot
            # consider refactoring one or both
            # the difference is that this function needs all the ballots
            ballots = Ballot.objects.filter(
                vote=vote,
                personvoter__in=voter_ids
            )

            # if there are no ballots max option will be None
            options_aggregated = ballots.values('option').aggregate(Max('option'))

            # this is a in memory only ballot object that is only constructed
            # for the serializer to use
            fake_ballot = Ballot(
                option=options_aggregated['option__max'],
                vote=vote,
            )

            # always append a ballot to party_ballots so that pagination returns
            # an expected number of objects, even if option is None
            party_ballots.append(fake_ballot)

        # serialize ballots
        ballot_serializer = BallotSerializer(
            party_ballots,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': ballot_serializer.data,
        }
