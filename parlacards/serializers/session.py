from rest_framework import serializers
from django.db.models import Q

from parlacards.serializers.common import CommonCachableSerializer, CommonOrganizationSerializer
from parladata.models.agenda_item import AgendaItem

class SessionSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, session):
        session_timestamp = session.updated_at
        organization_timestamps = session.organizations.all().values_list('updated_at', flat=True)
        timestamp = max([session_timestamp] + list(organization_timestamps))

        last_speech = session.speeches.all().order_by("updated_at").last()
        if last_speech:
            timestamp = max([timestamp, last_speech.updated_at])

        last_agenda_item = AgendaItem.objects.filter(session=session).order_by("updated_at").last()
        if last_agenda_item:
            timestamp = max([timestamp, last_agenda_item.updated_at])

        return f'SessionSerializer_{session.id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_has_transcript(self, session):
        return session.speeches.exists()

    def get_has_minutes(self, session):
        return AgendaItem.objects.filter(session=session).exists()

    def get_has_legislation(self, session):
        return session.legislation_considerations.filter(
            Q(timestamp__lte=self.context['date']) | Q(timestamp__isnull=True)
        ).exists()

    name = serializers.CharField()
    id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    organizations = CommonOrganizationSerializer(many=True)
    classification = serializers.CharField() # TODO regular, irregular, urgent, correspondent
    in_review = serializers.BooleanField()
    has_transcript = serializers.SerializerMethodField()
    has_minutes = serializers.SerializerMethodField()
    has_legislation = serializers.SerializerMethodField()
