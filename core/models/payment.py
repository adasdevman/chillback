from django.db import models
from django.conf import settings
from .base import TimeStampedModel
from .annonce import Annonce, Tarif
from django.core.exceptions import ValidationError
from uuid import uuid4

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
    transaction_id = models.CharField(max_length=100, blank=True, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'

    def __str__(self):
        return f"Paiement #{self.transaction_id} - {self.amount} FCFA par {self.user.email} ({self.status})"

    def clean(self):
        # Vérifier que le montant est positif
        if self.amount <= 0:
            raise ValidationError({'amount': 'Le montant doit être supérieur à 0'})
            
        # Vérifier que l'annonce est renseignée
        if not self.annonce:
            raise ValidationError({'annonce': 'L\'annonce est requise'})
            
        # Vérifier que le tarif est renseigné
        if not self.tarif:
            raise ValidationError({'tarif': 'Le tarif est requis'})
            
        # Vérifier que le tarif appartient bien à l'annonce
        if self.tarif and self.annonce and self.tarif.annonce != self.annonce:
            raise ValidationError({'tarif': 'Le tarif sélectionné n\'appartient pas à cette annonce'})

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Générer un ID de transaction unique
            self.transaction_id = f"TR-{str(uuid4())[:8]}"
        super().save(*args, **kwargs) 