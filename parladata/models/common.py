from django.db import models

# TODO razmisli kako bomo to uredili
# želimo imeti možnost, da je v eni bazi
# več sklicev
class Mandate(models.Model):
    """Mandate"""

    description = models.TextField(blank=True,
                                   null=True)

    def __str__(self):
        return self.description
