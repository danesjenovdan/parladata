from django.db import models
from parladata.behaviors.models import Timestampable

# TODO razmisli kako bomo to uredili
# želimo imeti možnost, da je v eni bazi
# več sklicev
class Mandate(models.Model):
    """Mandate"""

    description = models.TextField(blank=True, null=True)

    beginning = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.description


class EducationLevel(Timestampable):
    text = models.TextField()
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text

    class Meta(object):
        ordering = ['order']
