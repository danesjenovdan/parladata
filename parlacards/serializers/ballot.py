from rest_framework import serializers

from parlacards.serializers.motion import MotionSerializer
from parlacards.serializers.session import SessionSerializer

from parlacards.serializers.common import CommonSerializer

class BallotSerializer(CommonSerializer):
    def get_motion(self, obj):
        motion_serializer = MotionSerializer(obj.vote.motion)
        return motion_serializer.data
    
    def get_timestamp(self, obj):
        return obj.vote.timestamp
    
    def get_session(self, obj):
        session_serializer = SessionSerializer(obj.vote.motion.session)
        return session_serializer.data

    motion = serializers.SerializerMethodField()
    option = serializers.CharField()
    timestamp = serializers.SerializerMethodField()
    session = serializers.SerializerMethodField()
