from rest_framework import serializers

from parladata.models.speech import Speech
from parladata.models.ballot import Ballot
from parladata.models.question import Question

from parlacards.serializers.ballot import BallotSerializer
from parlacards.serializers.question import QuestionSerializer
from parlacards.serializers.common import CommonSerializer
from parlacards.serializers.session import SessionSerializer


class RecentActivitySpeechSerializer(CommonSerializer):
    speech_id = serializers.IntegerField(source='id')
    start_time = serializers.DateTimeField()
    session = SessionSerializer()


class EventSerializer(CommonSerializer):
    def to_representation(self, obj):
        # figure out which event type we're dealing with
        if isinstance(obj, Speech):
            event_type = 'speech'
            serializer = RecentActivitySpeechSerializer(
                obj,
                context=self.context
            )
        elif isinstance(obj, Ballot):
            event_type = 'ballot'
            serializer = BallotSerializer(
                obj,
                context=self.context
            )
        elif isinstance(obj, Question):
            event_type = 'question'
            serializer = QuestionSerializer(
                obj,
                context=self.context
            )
        else:
            raise ValueError(f'Cannot serialize {obj} as activity.')

        return {
            **serializer.data,
            'type': event_type
        }
