from rest_framework import serializers

from parlacards.serializers.common import CardSerializer, CommonOrganizationSerializer

class SessionSerializer(CardSerializer):
    name = serializers.CharField()
    gov_id = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    organizations = CommonOrganizationSerializer(many=True)
    classification = serializers.CharField()
    in_review = serializers.BooleanField()
