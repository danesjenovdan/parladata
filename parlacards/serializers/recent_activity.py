from rest_framework import serializers

from parladata.models.speech import Speech
from parladata.models.ballot import Ballot
from parladata.models.question import Question

from parlacards.serializers.speech import SpeechSerializer
from parlacards.serializers.ballot import BallotSerializer
# TODO
# from parlacards.serializers.question import QuestionSerializer
from parlacards.serializers.common import CommonSerializer

class RecentActivitySerializer(CommonSerializer):
    pass


class EventSerializer(CommonSerializer):
    def to_representation(self, obj):
        # figure out which event type we're dealing with
        if isinstance(obj, Speech):
            event_type = 'speech'
            serializer = SpeechSerializer(
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
            # TODO
            return event_type
        else:
            raise ValueError(f'Cannot serialize {obj} as activity.')

        return {
            **serializer.data,
            'type': event_type
        }


class DailyEventsSerializer(CommonSerializer):
    date = serializers.DateTimeField()
    events = EventSerializer(many=True)
