from django.db import models

from parladata.behaviors.models import Timestampable

import uuid


# Create your models here.
class NotificationUser(Timestampable):
    email = models.EmailField()
    hash = models.CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    latest_notification_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email


class Keyword(Timestampable):
    WIDE = "WIDE"
    NARROW = "NARROW"
    MATCHING_METHOD_CHOICES = {
        WIDE: "wide",
        NARROW: "narrow",
    }
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    FREQUENCY_CHOICES = {
        DAILY: "daily",
        WEEKLY: "weekly",
        MONTHLY: "monthly",
    }
    keyword = models.CharField(max_length=255)
    user = models.ForeignKey(
        NotificationUser, related_name="keywords", on_delete=models.CASCADE
    )
    matching_method = models.CharField(
        max_length=10,
        choices=MATCHING_METHOD_CHOICES.items(),
        default=WIDE,
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    notification_frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES.items(),
        default=DAILY,
    )
    latest_notification_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.keyword + " for " + self.user.email
