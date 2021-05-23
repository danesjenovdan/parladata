from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer

from parlacards.serializers.tag import TagSerializer

class MotionSerializer(CommonSerializer):
    id = serializers.CharField()
    tags = TagSerializer(many=True)
    text = serializers.CharField()
    result = serializers.CharField()
    classification = serializers.CharField()
