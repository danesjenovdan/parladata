from rest_framework import serializers

from parlacards.serializers.motion import MotionSerializer
from parlacards.serializers.session import SessionSerializer

from parlacards.serializers.common import CommonSerializer

# TODO
# class BallotSerializer(CommonCachableSerializer):
#     def calculate_cache_key(self, instance):
#         # instance is the vote
#         # TODO what if ballots change?
#         vote_timestamp = instance.vote.updated_at
#         person_timestamp = instance.personvoter.updated_at
#         ballot_timestamp = instance.updated_at
#         session_timestamp = instance.vote.motion.session.updated_at
#         timestamp = max([vote_timestamp, person_timestamp, ballot_timestamp, session_timestamp])
#         return f'BallotSerializer_{instance.id}_{instance.personvoter.id}_{timestamp.strftime("%Y-%m-%d-%H-%M-%s")}'

class BallotSerializer(CommonSerializer):
    def get_motion(self, obj):
        motion_serializer = MotionSerializer(
            obj.vote.motion,
            context=self.context
        )
        return motion_serializer.data
    
    def get_timestamp(self, obj):
        return obj.vote.timestamp
    
    def get_session(self, obj):
        session_serializer = SessionSerializer(
            obj.vote.motion.session,
            context=self.context
        )
        return session_serializer.data

    motion = serializers.SerializerMethodField()
    option = serializers.CharField()
    timestamp = serializers.SerializerMethodField()
    session = serializers.SerializerMethodField()
