from rest_framework import serializers

from parlacards.serializers.common import CardSerializer

class AreaSerializer(CardSerializer):
    name = serializers.CharField()
    classification = serializers.CharField()
