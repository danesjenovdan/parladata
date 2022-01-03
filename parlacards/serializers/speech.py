from rest_framework import serializers

from parlacards.serializers.session import SessionSerializer

from parlacards.serializers.common import CommonSerializer, CommonCachableSerializer, CommonPersonSerializer
from parlacards.serializers.vote import SpeechVoteSerializer

from parladata.models.vote import Vote


class BaseSpeechSerializer(CommonSerializer):
    # Use this when context['date'] should be the date of the speech.
    #
    # This is needed when using the CommonPersonSerializer or similar to return
    # the state of the person on the day of the speech, or when we need all the
    # groups/people active on the day of the speech.
    #
    # We should make a copy of the context object since we don't want to mess
    # with other serializers (a shallow copy here is good enough).
    #
    # TODO consider refactoring, this is very similar to _get_context_for_vote_date
    # in parlacards.serializers.vote
    def _get_context_for_speech_date(self, speech):
        new_context = dict.copy(self.context)
        new_context['date'] = speech.start_time
        return new_context

    def get_the_order(self, obj):
        # obj is the speech
        if obj.order:
            return obj.order
        return obj.id

    def get_votes(self, obj):
        votes = Vote.objects.filter(motion__speech=obj)
        return SpeechVoteSerializer(votes, many=True).data
    
    def get_person(self, speech):
        serializer = CommonPersonSerializer(
            speech.speaker,
            context=self._get_context_for_speech_date(speech)
        )

        return serializer.data

    id = serializers.IntegerField()
    content = serializers.CharField()
    the_order = serializers.SerializerMethodField()
    person = serializers.SerializerMethodField()
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
