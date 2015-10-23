from django.db.models import Q

__author__ = 'guglielmo'

from django.db import models
from datetime import datetime



class DateframeableQuerySet(models.query.QuerySet):
    """
    A custom ``QuerySet`` allowing easy retrieval of current, past and future instances
    of a Dateframeable model.

    Here, a *Dateframeable model* denotes a model class having an associated date range.

    """
    def past(self, moment=None):
        """
        Return a QuerySet containing the *past* instances of the model
        (i.e. those having an end date which is in the past).
        """
        if moment is None:
            moment = datetime.now()
        return self.filter(end_date__lte=moment)

    def future(self, moment=None):
        """
        Return a QuerySet containing the *future* instances of the model
        (i.e. those having a start date which is in the future).
        """
        if moment is None:
            moment = datetime.now()
        return self.filter(start_date__gte=moment)

    def current(self, moment=None):
        """
        Return a QuerySet containing the *current* instances of the model
        at the given moment in time, if the parameter is specified
        now if it is not
        """
        if moment is None:
            moment = datetime.now()

        return self.filter(Q(start_date__lte=moment) &
                           (Q(end_date__gte=moment) | Q(end_date__isnull=True)))



class PersonQuerySet(DateframeableQuerySet):
    pass

class OrganizationQuerySet(DateframeableQuerySet):
    pass

class PostQuerySet(DateframeableQuerySet):
    pass

class MembershipQuerySet(DateframeableQuerySet):
    pass

class ContactDetailQuerySet(DateframeableQuerySet):
    pass

class OtherNameQuerySet(DateframeableQuerySet):
    pass
