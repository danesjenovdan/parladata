from rest_framework import serializers

from parladata.models.link import Link
from parlacards.serializers.tag import TagSerializer


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = [
            "id",
            "url",
            "name",
            "tags",
        ]

    tags = TagSerializer(many=True)
