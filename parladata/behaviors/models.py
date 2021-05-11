from importlib import import_module

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from autoslug import AutoSlugField
from datetime import datetime
from django.utils.text import slugify
import uuid

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

class VersionableProperty(Versionable):
    owner = None
    value = models.TextField(blank=False, null=False)

    def __str__(self):
        return str(self.value)

    class Meta:
        abstract = True

class VersionableFieldsOwner(models.Model):
    @staticmethod
    def versionable_property_on_date(owner, property_model_name, datetime):
        versionable_properties_module = import_module('parladata.models.versionable_properties')
        PropertyModel = getattr(versionable_properties_module, property_model_name)
        active_properties = PropertyModel.objects.filter(
            models.Q(owner=owner),
            models.Q(valid_from__lte=datetime) | models.Q(valid_from__isnull=True),
            models.Q(valid_to__gte=datetime) | models.Q(valid_to__isnull=True),
        )

        if active_properties.count() > 1:
            # TODO maybe a more descriptive exception is appropriate
            raise Exception(f'More than one active {property_model_name} at {datetime}. Check your data.')
        
        active_property = active_properties.first()

        if not active_property:
            return None
        
        return active_property.value
    
    class Meta:
        abstract = True


class Taggable(models.Model):
    tags = TaggableManager()

    class Meta:
        abstract = True

class Sluggable(models.Model):
    def slug(self):
        if self.name:
            return slugify(f'{self.id}-{self.name}')
        return str(self.id)

    class Meta:
        abstract = True
