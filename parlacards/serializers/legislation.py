from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer

class LegislationSerializer(CommonSerializer):
    uid = serializers.CharField()
    text = serializers.CharField()
    epa = serializers.CharField()
    status = serializers.CharField()
    passed = serializers.BooleanField()
    classification = serializers.CharField()
    has_votes = serializers.BooleanField()
    has_abstract = serializers.BooleanField()
    timestamp = serializers.DateTimeField()
