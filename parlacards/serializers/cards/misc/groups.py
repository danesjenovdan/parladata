from importlib import import_module
from django.db.models import Q

from rest_framework import serializers

from parlacards.serializers.common import (
    CardSerializer,
    CommonOrganizationSerializer,
)

from parlacards.models import (
    GroupDiscord,
    GroupVocabularySize,
    GroupNumberOfQuestions,
    GroupVoteAttendance,
)
from parladata.models.memberships import PersonMembership

class GroupAnalysesSerializer(CommonOrganizationSerializer):
    def calculate_cache_key(self, group):
        all_analyses = (
            GroupDiscord,
            GroupVocabularySize,
            GroupNumberOfQuestions,
            GroupVoteAttendance,
        )

        analysis_timestamps = []
        for analysis in all_analyses:
            if analysis_object := analysis.objects.filter(group=group).order_by('-timestamp').first():
                analysis_timestamps.append(analysis_object.timestamp)

        last_membership = PersonMembership.objects.filter(Q(organization=group)|Q(on_behalf_of=group)).latest('updated_at')

        timestamp = max([group.updated_at, last_membership.updated_at, *analysis_timestamps])

        return f'GroupAnalysesSerializer_{group.id}_{timestamp.isoformat()}'

    def get_group_value(self, group, property_model_name):
        scores_module = import_module('parlacards.models')
        ScoreModel = getattr(scores_module, property_model_name)

        score_object = ScoreModel.objects.filter(
            group_id=group.id,
            timestamp__lte=self.context['date']
        ).order_by('-timestamp').first()

        if score_object:
            return score_object.value
        return None

    def get_results(self, obj):
        return {
            'seat_count': obj.number_of_members_at(self.context['date']),
            'intra_disunion': self.get_group_value(obj, 'GroupDiscord'),
            'number_of_amendments': None, # TODO
            'vocabulary_size': self.get_group_value(obj, 'GroupVocabularySize'),
            'number_of_questions': self.get_group_value(obj, 'GroupNumberOfQuestions'),
            'vote_attendance': self.get_group_value(obj, 'GroupVoteAttendance'),
        }

    results = serializers.SerializerMethodField()


class MiscGroupsCardSerializer(CardSerializer):
    def get_results(self, parent_organization):
        serializer = GroupAnalysesSerializer(
            parent_organization.query_parliamentary_groups(self.context['date']),
            many=True,
            context=self.context
        )
        return serializer.data
