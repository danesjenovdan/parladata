from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer
from parlacards.serializers.vote import BareVoteSerializer
from parlacards.serializers.link import LinkSerializer

from parladata.models.vote import Vote
from parladata.models.link import Link

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

    def get_status(self, obj):
        return obj.status.name


class LegislationDetailSerializer(LegislationSerializer):
    votes = serializers.SerializerMethodField()
    abstract = serializers.CharField()
    documents = serializers.SerializerMethodField()

    def get_votes(self, obj):
        votes = Vote.objects.filter(motion__law=obj)
        return BareVoteSerializer(
            votes,
            many=True,
            context=self.context
        ).data

    def get_documents(self, obj):
        links = Link.objects.filter(motion__law=obj)
        return LinkSerializer(
            links,
            many=True,
            context=self.context
        ).data

