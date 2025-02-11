from django.db import models
from django.conf import settings
from .base import TimeStampedModel

class Notification(TimeStampedModel):
    NOTIFICATION_TYPES = (
        ('payment', 'Paiement'),
        ('account', 'Compte'),
        ('validation', 'Validation'),
        ('other', 'Autre')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='other'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['user', '-created']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f"{self.type} - {self.title} ({self.user.email})"

    def mark_as_read(self):
        if not self.read:
            self.read = True
            self.save() 