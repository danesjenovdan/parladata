from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField
from autoslug import AutoSlugField
from datetime import datetime

from taggit.managers import TaggableManager

__author__ = 'guglielmo'


class GenericRelatable(models.Model):
    """
    An abstract class that provides the possibility of generic relations
    """
    content_type = models.ForeignKey(ContentType,
                                     related_name='%(app_label)s_%(class)s_related')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True


class Timestampable(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created_at = AutoCreatedField(_('creation time'))
    updated_at = AutoLastModifiedField(_('last modification time'))

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

class Permalinkable(models.Model):
    """
    An abstract base class model that provides a unique slug,
    and the methods necessary to handle the permalink
    """
    from django.utils.text import slugify

    slug = AutoSlugField(
        populate_from=lambda instance: instance.slug_source,
        unique=True,
        slugify=slugify
    )

    class Meta:
        abstract = True

    def get_url_kwargs(self, **kwargs):
        kwargs.update(getattr(self, 'url_kwargs', {}))
        return kwargs

    @models.permalink
    def get_absolute_url(self):
        url_kwargs = self.get_url_kwargs(slug=self.slug)
        return (self.url_name, (), url_kwargs)
class Taggable(models.Model):
    tags = TaggableManager()

    class Meta:
        abstract = True

