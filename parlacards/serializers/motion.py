from rest_framework import serializers

from parlacards.serializers.common import CardSerializer

from parlacards.serializers.tag import TagSerializer

class MotionSerializer(CardSerializer):
    id = serializers.CharField()
    tags = TagSerializer(many=True)
    text = serializers.CharField()
    result = serializers.CharField()
    classification = serializers.CharField()
