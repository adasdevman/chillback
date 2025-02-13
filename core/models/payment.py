from django.db import models
from django.conf import settings
from .base import TimeStampedModel
from .annonce import Annonce, Tarif

class Payment(TimeStampedModel):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé')
    )

    PAYMENT_TYPE_CHOICES = (
        ('ticket', 'Ticket'),
        ('table', 'Table'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_payments'
    )
    annonce = models.ForeignKey(
        Annonce,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments'
    )
    tarif = models.ForeignKey(
        Tarif,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'

    def __str__(self):
        return f"Paiement de {self.amount} FCFA par {self.user.email} ({self.status})" 