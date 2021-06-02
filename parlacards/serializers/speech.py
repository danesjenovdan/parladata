from rest_framework import serializers

from parlacards.serializers.session import SessionSerializer

from parlacards.serializers.common import CommonSerializer, CommonPersonSerializer

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

    speech_id = serializers.IntegerField(source='id')
    content = serializers.CharField()
    session = SessionSerializer()
    the_order = serializers.SerializerMethodField()
    quoted_text = serializers.SerializerMethodField()
    start_idx = serializers.SerializerMethodField()
    end_idx = serializers.SerializerMethodField()
    quote_id = serializers.SerializerMethodField()
    person = CommonPersonSerializer(source='speaker')
