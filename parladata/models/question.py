from django.db import models

from parladata.behaviors.models import Timestampable

class Question(Timestampable):
    """All questions from members of parlament."""

    session = models.ForeignKey('Session',
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE,
                                help_text='The session this question belongs to.')

    timestamp = models.DateTimeField(blank=True,
                               null=True,
                               help_text='Date of the question.')

    answer_timestamp = models.DateTimeField(blank=True,
                                         null=True,
                                         help_text='Date of answer the question.')

    title = models.TextField(blank=True,
                             null=True,
                             help_text='Title name as written on dz-rs.si')

    authors = models.ManyToManyField('Person',
                                     blank=True,
                                     help_text='The persons (MP) who asked the question.')

    recipient_people = models.ManyToManyField('Person',
                                              blank=True,
                                              help_text='Recipient person (if it\'s a person).',
                                              related_name='questions')

    recipient_organizations = models.ManyToManyField('Organization',
                                                    blank=True,
                                                    help_text='Recipient organization (if it\'s an organization).',
                                                    related_name='questions_org')

    recipient_text = models.TextField(blank=True,
                                      null=True,
                                      help_text='Recipient name as written on dz-rs.si')

    # TODO make this into a choice field
    type_of_question = models.TextField(blank=True,
                                   null=True)

    def __str__(self):
        author_names = [author.name for author in self.authors.all()]
        return ' '.join(author_names)
