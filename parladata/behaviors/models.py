from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from autoslug import AutoSlugField
from datetime import datetime

from taggit.managers import TaggableManager

class Parsable(models.Model):
    parser_names = models.TextField(blank=True, null=True)

    def add_parser_name(self, new_parser_name):
        if not self.parser_names:
            self.parser_names = new_parser_name
        else:
            self.parser_names = f'{self.parser_names}|{new_parser_name}'
    
    @property
    def parser_names_as_list(self):
        if not self.parser_names:
            return []
        else:
            return self.parser_names.split('|')

    class Meta:
        abstract = True


class Timestampable(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

class Versionable(models.Model):
    """
    An abstract base class model that provides versioning fields
    ``valid_from`` and ``valid_to``
    """

    valid_from = models.DateTimeField(
        help_text=_('row valid from'),
        blank=True,
        null=True,
        default=None
    )
    valid_to = models.DateTimeField(
        help_text=_('row valid to'),
        blank=True,
        null=True,
        default=None
    )

    class Meta:
        abstract = True


class Taggable(models.Model):
    tags = TaggableManager()

    class Meta:
        abstract = True

