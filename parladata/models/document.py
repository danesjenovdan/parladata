from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable, Taggable


class Document(Timestampable, Taggable):
    file = models.FileField()
    name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
