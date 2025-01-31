from django.db import models # type: ignore
from django.conf import settings
from users.models import User
from events.models import Annonce # type: ignore

class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('COMPLETED', 'Complété'),
        ('FAILED', 'Échoué'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('CINETPAY', 'CinetPay'),
        ('ORANGE_MONEY', 'Orange Money'),
        ('MOOV_MONEY', 'Moov Money'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='payments_app_payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'

    def __str__(self):
        return f"Paiement {self.transaction_id} - {self.amount} FCFA"
