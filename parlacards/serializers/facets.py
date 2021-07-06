from rest_framework import serializers

from .common import CommonOrganizationSerializer, CommonSerializer


class GroupFacetSerializer(CommonSerializer):
    group = CommonOrganizationSerializer()
    value = serializers.IntegerField()
