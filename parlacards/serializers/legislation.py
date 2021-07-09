from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer
from parlacards.serializers.vote import SessionVoteSerializer

from parladata.models.vote import Vote

class LegislationSerializer(CommonSerializer):
    id = serializers.IntegerField()
    uid = serializers.CharField()
    text = serializers.CharField()
    epa = serializers.CharField()
    status = serializers.CharField()
    passed = serializers.BooleanField()
    classification = serializers.CharField()
    has_votes = serializers.BooleanField()
    has_abstract = serializers.BooleanField()
    timestamp = serializers.DateTimeField()


class LegislationDetailSerializer(LegislationSerializer):
    votes = serializers.SerializerMethodField()

    def get_votes(self, obj):
        votes = Vote.objects.filter(motion__law=obj)
        return SessionVoteSerializer(
            votes,
            many=True,
            context=self.context
        ).data

