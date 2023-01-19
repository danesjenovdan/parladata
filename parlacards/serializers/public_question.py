from rest_framework import serializers

from parladata.models.public_question import PublicPersonQuestion, PublicPersonAnswer

from drf_recaptcha.fields import ReCaptchaV3Field


class PublicPersonAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicPersonAnswer
        fields = ('id', 'created_at', 'approved_at', 'text')


class PublicPersonQuestionSerializer(serializers.ModelSerializer):
    recaptcha = ReCaptchaV3Field(action="PublicPersonQuestion", required=False)
    answer = serializers.SerializerMethodField()
    class Meta:
        model = PublicPersonQuestion
        fields = ('answer', 'recaptcha', 'id', 'created_at', 'approved_at', 'text')
        extra_kwargs = {
            'author_email': {'write_only': True},
            'recipient_person': {'write_only': True},
            'author': {'write_only': True},
            'approved_at': {'read_only': True},
        }


    def get_answer(self, obj):
        return PublicPersonAnswerSerializer(obj.answer.filter(approved_at__isnull=False).first()).data

    def validate(self, data):
        data.pop("recaptcha")
        return data
