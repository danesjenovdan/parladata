from django.db import models

from parladata.behaviors.models import Timestampable, Approvable


class PublicPersonQuestion(Timestampable, Approvable):
    recipient_person = models.ForeignKey(
        'Person',
        help_text='Recipient person.',
        related_name='received_person_questions',
        on_delete=models.CASCADE
    )
    author_email = models.EmailField(max_length=256, blank=True, null=True)
    text = models.TextField(
        help_text='Text of question'
    )
    notification_set_at = models.DateTimeField(null=True, blank=True, db_index=True)

    def __str__(self):
        return f'{self.recipient_person.name} - {self.text[:50]}'


class PublicPersonAnswer(Timestampable, Approvable):
    question = models.ForeignKey(
        'PublicPersonQuestion',
        on_delete=models.PROTECT,
        related_name='answer')
    text = models.TextField(
        help_text='Text of answer'
    )
    notification_set_at = models.DateTimeField(null=True, blank=True, db_index=True)

    def __str__(self):
        return f'{self.question.recipient_person.name} - {self.text[:50]}'
