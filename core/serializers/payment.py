from rest_framework import serializers
from ..models import Payment, Annonce, Tarif
from .base import TimeStampedModelSerializer
from .annonce import AnnonceListSerializer

class PaymentSerializer(TimeStampedModelSerializer):
    annonce = AnnonceListSerializer(read_only=True)
    annonce_id = serializers.IntegerField(write_only=True, source='annonce')
    tarif_id = serializers.IntegerField(write_only=True, source='tarif')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    billing_info = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'annonce', 'annonce_id', 'amount', 'status', 'status_display',
            'payment_type', 'payment_type_display', 'transaction_id',
            'description', 'created', 'modified', 'tarif', 'tarif_id', 'billing_info',
            'user_first_name', 'user_last_name', 'user_email',
            'user_phone', 'user_address', 'user_city',
            'annonce_titre', 'annonce_categorie', 'annonce_sous_categorie',
            'annonce_utilisateur_id', 'tarif_nom', 'tarif_prix'
        ]
        read_only_fields = ['user', 'transaction_id', 'created', 'modified']

    def create(self, validated_data):
        # Remove billing_info from validated_data if present
        billing_info = validated_data.pop('billing_info', None) or self.context.get('billing_info', {})
        
        # Initialize default values for required fields
        validated_data.setdefault('annonce_titre', 'Non spécifié')
        validated_data.setdefault('annonce_categorie', 'Non spécifié')
        validated_data.setdefault('annonce_sous_categorie', '')
        validated_data.setdefault('annonce_utilisateur_id', 0)
        validated_data.setdefault('tarif_nom', 'Non spécifié')
        validated_data.setdefault('tarif_prix', 0)
        
        # Try to fetch and populate announcement details
        try:
            annonce_id = validated_data.get('annonce')
            if annonce_id:
                annonce = Annonce.objects.select_related('categorie', 'sous_categorie').get(id=annonce_id)
                validated_data['annonce_titre'] = annonce.titre
                validated_data['annonce_categorie'] = annonce.categorie.nom if annonce.categorie else 'Non spécifié'
                validated_data['annonce_sous_categorie'] = annonce.sous_categorie.nom if annonce.sous_categorie else ''
                validated_data['annonce_utilisateur_id'] = annonce.utilisateur_id
        except Exception as e:
            print(f"Error fetching announcement details: {e}")

        # Try to fetch and populate tarif details
        try:
            tarif_id = validated_data.get('tarif')
            if tarif_id:
                tarif = Tarif.objects.get(id=tarif_id)
                validated_data['tarif_nom'] = tarif.nom
                validated_data['tarif_prix'] = tarif.prix
                # Set amount if not provided
                if 'amount' not in validated_data:
                    validated_data['amount'] = tarif.prix
        except Exception as e:
            print(f"Error fetching tarif details: {e}")
        
        # Update user information from billing info
        if billing_info:
            validated_data.update({
                'user_first_name': billing_info.get('customer_name', 'Non spécifié'),
                'user_last_name': billing_info.get('customer_surname', 'Non spécifié'),
                'user_email': billing_info.get('customer_email', 'no-email@example.com'),
                'user_phone': billing_info.get('customer_phone_number', ''),
                'user_address': billing_info.get('customer_address', ''),
                'user_city': billing_info.get('customer_city', ''),
            })
        else:
            validated_data.update({
                'user_first_name': 'Non spécifié',
                'user_last_name': 'Non spécifié',
                'user_email': 'no-email@example.com',
                'user_phone': '',
                'user_address': '',
                'user_city': '',
            })

        # Set the user from the context
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user

        print("Final validated data:", validated_data)  # Debug print
        
        # Create the payment instance
        instance = super().create(validated_data)
        return instance