from rest_framework import serializers

from parlacards.serializers.session import SessionSerializer

from parlacards.serializers.common import CommonCachableSerializer
from parlacards.serializers.speech import SpeechSerializer
from parlacards.models import Quote


class QuoteWithSessionSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        # instance is the qoute
        # TODO prefetch speech speaker session on parent obj
        quote_timestamp = instance.updated_at
        speech_timestamp = instance.speech.updated_at
        person_timestamp = instance.speech.speaker.updated_at
        session_timestamp = instance.speech.session.updated_at

        timestamp = max([speech_timestamp, person_timestamp, session_timestamp, quote_timestamp])
        return f'QuoteWithSessionSerializer_{instance.id}_{timestamp.isoformat()}'

    def get_session(self, obj):
        # obj is the quote
        serializer = SessionSerializer(
            obj.speech.session,
            context=self.context
        )
        return serializer.data

    session = serializers.SerializerMethodField()
    speech = SpeechSerializer()
    quote_content = serializers.CharField()
    start_index = serializers.IntegerField()
    end_index = serializers.IntegerField()


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = '__all__'

    def validate(self, data):
        data = super().validate(data)
        if data['quote_content'] != data['speech'].content[data['start_index']:data['end_index']]:
            raise serializers.ValidationError({'quote_content': 'Quote content doesn`t match speech content'})
        return data
