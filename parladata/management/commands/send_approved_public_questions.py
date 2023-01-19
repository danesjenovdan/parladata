from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils import translation

from parladata.models.public_question import PublicPersonQuestion
from parladata.update_utils import send_email

from datetime import datetime


class Command(BaseCommand):
    help = 'Send public questions emails'

    def handle(self, *args, **options):
        questions = PublicPersonQuestion.objects.filter(
            notification_sent_at__isnull=True, approved_at__isnull=False
        ).exclude(
            rejected_at__isnull=False
        )
        for question in questions:
            email = question.recipient_person.email
            if email:
                translation.activate(settings.EMAIL_LANGUAGE_CODE)
                send_email(
                    f'#{question.id} ' + _('Question from Parlameter'),
                    email,
                    'public_question_email.html',
                    {
                        'text': question.text,
                    },
                    reply_to=settings.REPLY_TO_EMAIL
                )
                question.notification_sent_at = datetime.now()
                question.save()
