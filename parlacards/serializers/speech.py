from rest_framework import serializers

from parlacards.serializers.session import SessionSerializer

from parlacards.serializers.common import CommonSerializer, CommonCachableSerializer, CommonPersonSerializer
from parlacards.serializers.vote import SpeechVoteSerializer

from parladata.models.vote import Vote


class BaseSpeechSerializer(CommonSerializer):
    def get_the_order(self, obj):
        # obj is the speech
        if obj.order:
            return obj.order
        return obj.id

    def get_votes(self, obj):
        votes = Vote.objects.filter(motion__speech=obj)
        return SpeechVoteSerializer(votes, many=True).data

    id = serializers.IntegerField()
    content = serializers.CharField()
    the_order = serializers.SerializerMethodField()
    person = CommonPersonSerializer(source='speaker')
    start_time = serializers.DateTimeField()
    votes = serializers.SerializerMethodField()


class SpeechSerializer(BaseSpeechSerializer, CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        # instance is the speech
        speech_timestamp = instance.updated_at
        person_timestamp = instance.speaker.updated_at
        try:
            vote_timestamp = Vote.objects.filter(
                motion__speech=instance
            ).latest(
                'updated_at'
            ).updated_at
        except Vote.DoesNotExist:
            vote_timestamp = speech_timestamp

        timestamp = max([speech_timestamp, person_timestamp, vote_timestamp])
        return f'SpeechSerializer_{instance.id}_{timestamp.isoformat()}'


class BaseSpeechWithSessionSerializer(BaseSpeechSerializer):
    def get_session(self, obj):
        # obj is the speech
        serializer = SessionSerializer(
            obj.session,
            context=self.context
        )
        return serializer.data

    session = serializers.SerializerMethodField()


class SpeechWithSessionSerializer(BaseSpeechWithSessionSerializer, CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        # instance is the speech
        speech_timestamp = instance.updated_at
        person_timestamp = instance.speaker.updated_at
        session_timestamp = instance.session.updated_at
        try:
            vote_timestamp = Vote.objects.filter(
                motion__speech=instance
            ).latest(
                'updated_at'
            ).updated_at
        except Vote.DoesNotExist:
            vote_timestamp = speech_timestamp

        timestamp = max([speech_timestamp, person_timestamp, session_timestamp, vote_timestamp])
        return f'SpeechWithSessionSerializer_{instance.id}_{timestamp.isoformat()}'


class HighlightSerializer(BaseSpeechWithSessionSerializer):
    pass
