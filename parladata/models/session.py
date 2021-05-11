from django.db import models

from parladata.behaviors.models import Timestampable

class Session(Timestampable):
    """Sessions that happened in parliament."""

    mandate = models.ForeignKey('Mandate',
                                blank=False, null=False,
                                on_delete=models.CASCADE,
                                help_text='The mandate of this session.')

    name = models.TextField(blank=False, null=False,
                            help_text='Session name')

    gov_id = models.TextField(blank=True, null=True,
                              help_text='Gov website ID.')

    start_time = models.DateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = models.DateTimeField(blank=True, null=True,
                                   help_text='End time')

    organizations = models.ManyToManyField('Organization',
                                           related_name='sessions',
                                           help_text='The organization(s) in session')

    classification = models.CharField(max_length=128,
                                      blank=True, null=True,
                                      help_text='Session classification')

    in_review = models.BooleanField(default=False,
                                    help_text='Is session still in review?')

    @property
    def organization(self):
        if self.organizations.all().count() > 1:
            raise Exception('This session belongs to multiple organizations. Use the plural form "organizations".')
        
        return self.organizations.first()

    def __str__(self):
        if self and self.organization:
          return str(self.name) + ",  " + str(self.organization.name)
        else:
          return "Session"
