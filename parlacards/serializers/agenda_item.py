from rest_framework import serializers
from django.db.models import Q

from parladata.models.agenda_item import AgendaItem

from parlacards.serializers.common import CommonCachableSerializer, CommonSerializer

from parlacards.serializers.tag import TagSerializer
from parlacards.serializers.link import LinkSerializer

class AgendaItemSerializer(CommonSerializer):
    id = serializers.IntegerField()
    tags = TagSerializer(many=True)
    name = serializers.CharField()
    order = serializers.IntegerField()
    text = serializers.CharField()
    documents = serializers.SerializerMethodField()

    def get_documents(self, obj):
        return LinkSerializer(
            obj.links.all().exclude(tags__name='vote-pdf').order_by('id'),
            many=True
        ).data


class AgendaItemsSerializer(CommonCachableSerializer):
    agenda_items = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    def calculate_cache_key(self, instance):
        # instance is the session
        return f'AgendaItemSerializer{instance.id}_{instance.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_agenda_items(self, obj):
        agenda_item_serializer = AgendaItemSerializer(
            AgendaItem.objects.filter(
                Q(datetime__lte=self.context['date']) | Q(datetime__isnull=True),
                session=obj,
            ).order_by('order'),
            context=self.context,
            many=True
        )
        return agenda_item_serializer.data

    def get_documents(self, obj):
        return LinkSerializer(
            obj.links.all().exclude(tags__name='vote-pdf').order_by('id'),
            many=True
        ).data
