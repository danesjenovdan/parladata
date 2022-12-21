from rest_framework import serializers

from parladata.models.public_question import PublicPersonQuestion

from drf_recaptcha.fields import ReCaptchaV3Field


class PublicPersonQuestionSerializer(serializers.ModelSerializer):
    recaptcha = ReCaptchaV3Field(action="PublicPersonQuestion", required=False)
    class Meta:
        model = PublicPersonQuestion
        exclude = ('rejected_at', 'notification_set_at')
        read_only_fields = ('is_active', 'is_staff')
        extra_kwargs = {
            'author_email': {'write_only': True},
            'recipient_person': {'write_only': True},
            'author': {'write_only': True},
            'approved_at': {'read_only': True},
        }

    def validate(self, data):
        data.pop("recaptcha")
        return data
