from rest_framework.serializers import CharField

from parlacards.serializers.common import CardSerializer

class OrganizationSerializer(CardSerializer):
    name = CharField()
    slug = CharField()
