from rest_framework import serializers

from parladata.models.link import Link

from parlacards.serializers.common import CardSerializer, VersionableSerializerField, CommonPersonSerializer, CommonOrganizationSerializer


class OrganizationSerializer(CommonOrganizationSerializer):
    # TODO this will return all links they
    # should be filtered to only contain
    # social networks
    def get_social_networks(self, obj):
        links = Link.objects.filter(organization=obj)
        return {link.note: link.url for link in links}

    def get_presidents(self, obj):
        presidents = obj.query_people_by_role('president')
        serializer = CommonPersonSerializer(presidents, many=True, context=self.context)
        return serializer.data

    def get_deputies(self, obj):
        deputies = obj.query_people_by_role('president')
        serializer = CommonPersonSerializer(deputies, many=True, context=self.context)
        return serializer.data

    number_of_members = serializers.IntegerField()
    # number_of_organization_members = serializersIntegerField()
    social_networks = serializers.SerializerMethodField()
    presidents = serializers.SerializerMethodField()
    deputies = serializers.SerializerMethodField()

class OrganizationMembersSerializer(CommonOrganizationSerializer):
    def get_members(self, obj):
        serializer = CommonPersonSerializer(obj.members, many=True, context=self.context)
        return serializer.data

    members = serializers.SerializerMethodField()
