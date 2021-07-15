from rest_framework import serializers

from parlacards.serializers.common import CommonCachableSerializer

from parlacards.serializers.tag import TagSerializer

class MotionSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        # instance is the vote
        return f'MotionSerializer{instance.id}_{instance.updated_at.strftime("%Y-%m-%d-%H-%M-%s")}'

    id = serializers.CharField()
    tags = TagSerializer(many=True)
    text = serializers.CharField()
    result = serializers.CharField()
    classification = serializers.CharField()
