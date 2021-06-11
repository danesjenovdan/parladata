from rest_framework import serializers

from parladata.models.link import Link

from parlacards.serializers.common import (
    CommonPersonSerializer,
    CommonOrganizationSerializer,
)


class OrganizationSerializer(CommonOrganizationSerializer):
    # TODO this will return all links they
    # should be filtered to only contain
    # social networks
    def get_social_networks(self, obj):
        links = Link.objects.filter(organization=obj)
        return {link.note: link.url for link in links}

    def get_presidents(self, obj):
        presidents = obj.query_members_by_role('president')
        serializer = CommonPersonSerializer(presidents, many=True, context=self.context)
        return serializer.data

    def get_deputies(self, obj):
        deputies = obj.query_members_by_role('president')
        serializer = CommonPersonSerializer(deputies, many=True, context=self.context)
        return serializer.data

    def get_number_of_members(self, obj):
        return obj.number_of_members_at(self.context['date'])

    def get_members(self, obj):
        members = obj.query_members_by_role(role='member', timestamp=self.context['date'])
        return CommonPersonSerializer(members, many=True, context=self.context).data

    number_of_members = serializers.SerializerMethodField()
    social_networks = serializers.SerializerMethodField()
    email = serializers.CharField()
    presidents = serializers.SerializerMethodField()
    deputies = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()


class MembersSerializer(CommonOrganizationSerializer):
    def get_members(self, obj):
        serializer = CommonPersonSerializer(obj.query_members(timestamp=self.context['date']), many=True, context=self.context)
        return serializer.data

    members = serializers.SerializerMethodField()
