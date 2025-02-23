from rest_framework import serializers
from ..models import Payment
from .base import TimeStampedModelSerializer
from .annonce import AnnonceListSerializer

class PaymentSerializer(TimeStampedModelSerializer):
    annonce = AnnonceListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'annonce', 'amount', 'status', 'status_display',
            'payment_type', 'payment_type_display', 'transaction_id',
            'description', 'created', 'modified'
        ]
        read_only_fields = ['user', 'transaction_id'] 