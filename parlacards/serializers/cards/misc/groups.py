from importlib import import_module

from rest_framework import serializers

from parlacards.serializers.common import (
    CardSerializer,
    CommonOrganizationSerializer,
)

class GroupAnalysesSerializer(CommonOrganizationSerializer):
    def calculate_cache_key(self, instance):
        return f'GroupAnalysesSerializer_{instance.id}_{instance.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

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
