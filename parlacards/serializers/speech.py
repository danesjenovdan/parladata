from rest_framework import serializers

from parlacards.serializers.session import SessionSerializer

from parlacards.serializers.common import CommonSerializer, CommonPersonSerializer
from parlacards.serializers.vote import SpeechVoteSerializer

from parladata.models.vote import Vote

class SpeechSerializer(CommonSerializer):
    def get_the_order(self, obj):
        # obj is the speech
        if obj.order:
            return obj.order
        return obj.id
    
    def get_quoted_text(self, obj):
        return None
    
    def get_start_idx(self, obj):
        return None
    
    def get_end_idx(self, obj):
        return None
    
    def get_quote_id(self, obj):
        return None

    def get_votes(self, obj):
        votes = Vote.objects.filter(motion__speech=obj)
        return SpeechVoteSerializer(votes, many=True).data

    the_order = serializers.SerializerMethodField()
    quoted_text = serializers.SerializerMethodField()
    start_idx = serializers.SerializerMethodField()
    end_idx = serializers.SerializerMethodField()
    quote_id = serializers.SerializerMethodField()
    person = CommonPersonSerializer(source='speaker')
    start_time = serializers.DateTimeField()
    votes = serializers.SerializerMethodField()
