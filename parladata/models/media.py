from django.db import models
from django.utils.translation import ugettext_lazy as _

from parladata.behaviors.models import Timestampable


class Medium(Timestampable):
    name = models.TextField(
        verbose_name=_('name'),
        help_text=_('Medium name'),
    )

    url = models.URLField(
        max_length=255,
        verbose_name=_('url'),
        help_text=_('Medium URL'),
    )

    active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
    )

    def __str__(self):
        return self.name


class MediaReport(Timestampable):
    title = models.TextField(
        verbose_name=_('title'),
        help_text=_('Report title'),
    )

    url = models.URLField(
        max_length=500,
        verbose_name=_('url'),
        help_text=_('Report URL'),
    )

    report_date = models.DateField()

    retrieval_date = models.DateTimeField()

    medium = models.ForeignKey(
        Medium,
        on_delete=models.CASCADE,
        related_name='reports',
    )

    mentioned_people = models.ManyToManyField(
        'Person',
        blank=True,
        related_name='media_reports',
    )

    mentioned_organizations = models.ManyToManyField(
        'Organization',
        blank=True,
        related_name='media_reports',
    )

    mentioned_legislation = models.ManyToManyField(
        'Law',
        blank=True,
        related_name='media_reports',
    )

    mentioned_motions = models.ManyToManyField(
        'Motion',
        blank=True,
        related_name='media_reports',
    )

    mentioned_votes = models.ManyToManyField(
        'Vote',
        blank=True,
        related_name='media_reports',
    )

    def __str__(self):
        return self.title
