from rest_framework import serializers

from parladata.models.common import Mandate

from parlacards.serializers.common import CommonSerializer

class MandateSerializer(CommonSerializer):
    id = serializers.IntegerField()
    description = serializers.TextField()
    beginning = serializers.DateTimeField()
