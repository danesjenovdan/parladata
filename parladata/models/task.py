from datetime import datetime

from django.db import models

from parladata.behaviors.models import Timestampable, Taggable


class Task(Timestampable, Taggable):
    started_at = models.DateTimeField(
        help_text='time when started',
        blank=True,
        null=True,
        default=None
    )
    finished_at = models.DateTimeField(
        help_text='time when finished',
        blank=True,
        null=True,
        default=None
    )
    errored_at = models.DateTimeField(
        help_text='time when errored',
        blank=True,
        null=True,
        default=None
    )
    name = models.TextField(blank=False, null=False, help_text='Name of task')
    payload = models.JSONField(default={}, help_text='Payload kwargs')
