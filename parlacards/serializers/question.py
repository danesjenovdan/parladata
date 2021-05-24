from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer, CommonPersonSerializer

class QuestionSerializer(CommonSerializer):
    def get_recipient_people(self, obj):
        return CommonPersonSerializer(obj.recipient_people.all(), context=self.context, many=True).data

    def get_authors(self, obj):
        return CommonPersonSerializer(obj.authors.all(), context=self.context, many=True).data

    # TODO check which fields we need
    timestamp = serializers.DateTimeField()
    answer_timestamp = serializers.DateTimeField()
    title = serializers.CharField()
    authors = serializers.SerializerMethodField()
    recipient_people = serializers.SerializerMethodField()
    recipient_text = serializers.CharField()
