from rest_framework import serializers

from parlacards.serializers.motion import MotionSerializer

from parlacards.serializers.common import CommonSerializer

class BallotSerializer(CommonSerializer):
    def get_motion(self, obj):
        motion_serializer = MotionSerializer(obj.vote.motion)
        return motion_serializer.data
    
    def get_timestamp(self, obj):
        return obj.vote.timestamp

    motion = serializers.SerializerMethodField()
    option = serializers.CharField()
    timestamp = serializers.SerializerMethodField()