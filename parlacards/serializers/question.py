from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer, CommonPersonSerializer

class QuestionSerializer(CommonSerializer):
    def get_recipient_person(self, obj):
        return CommonPersonSerializer(obj.recipient_person.all(), context=self.context, many=True).data

    def get_authors(self, obj):
        return CommonPersonSerializer(obj.authors.all(), context=self.context, many=True).data

    timestamp = serializers.DateTimeField()
    answer_timestamp = serializers.DateTimeField()
    title = serializers.CharField()
    authors = serializers.SerializerMethodField()
    recipient_person = serializers.SerializerMethodField()
    recipient_text = serializers.CharField()
