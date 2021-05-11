from rest_framework.serializers import CharField

from parlacards.serializers.common import CardSerializer

class AreaSerializer(CardSerializer):
    name = CharField()
    classification = CharField()
