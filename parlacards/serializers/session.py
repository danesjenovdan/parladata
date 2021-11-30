from rest_framework import serializers

from parlacards.serializers.common import CommonCachableSerializer, CommonOrganizationSerializer

class SessionSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        # instance is session
        session_timestamp = instance.updated_at
        organization_timestamps = instance.organizations.all().values_list('updated_at', flat=True)
        timestamp = max([session_timestamp] + list(organization_timestamps))
        return f'SessionSerializer_{instance.id}_{timestamp.strftime("%Y-%m-%d-%H-%M-%s")}'

    def get_has_transcript(self, obj):
        # obj is the session
        return obj.speeches.exists()

    name = serializers.CharField()
    id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    organizations = CommonOrganizationSerializer(many=True)
    classification = serializers.CharField() # TODO regular, irregular, urgent, correspondent
    in_review = serializers.BooleanField()
    has_transcript = serializers.SerializerMethodField()
