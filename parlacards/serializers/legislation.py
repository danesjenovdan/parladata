from rest_framework import serializers

from parlacards.serializers.common import CardSerializer

class LegislationSerializer(CardSerializer):
    uid = serializers.CharField()
    text = serializers.CharField()
    epa = serializers.CharField()
    status = serializers.CharField()
    passed = serializers.BooleanField()
    law_type = serializers.CharField()
    has_votes = serializers.BooleanField()
    has_abstract = serializers.BooleanField()
