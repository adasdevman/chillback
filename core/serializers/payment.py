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
        read_only_fields = [
            'user', 'transaction_id', 'created', 'modified',
            'user_first_name', 'user_last_name', 'user_email',
            'user_phone', 'user_address', 'user_city',
            'annonce_titre', 'annonce_categorie', 'annonce_sous_categorie',
            'annonce_utilisateur_id', 'tarif_nom', 'tarif_prix'
        ]

    def validate(self, data):
        # Validate amount is positive
        amount = data.get('amount')
        if amount and amount <= 0:
            raise serializers.ValidationError({'amount': 'Le montant doit être supérieur à 0'})

        # Validate annonce exists
        annonce_id = data.get('annonce')
        if annonce_id:
            try:
                annonce = Annonce.objects.get(id=annonce_id)
                if not annonce.est_actif:
                    raise serializers.ValidationError({'annonce': 'Cette annonce n\'est pas active'})
            except Annonce.DoesNotExist:
                raise serializers.ValidationError({'annonce': 'Annonce invalide'})

        # Validate tarif exists and belongs to the annonce
        tarif_id = data.get('tarif')
        if tarif_id:
            try:
                tarif = Tarif.objects.get(id=tarif_id)
                if annonce_id and tarif.annonce.id != annonce_id:
                    raise serializers.ValidationError({'tarif': 'Le tarif sélectionné n\'appartient pas à cette annonce'})
                # Set amount if not provided
                if 'amount' not in data:
                    data['amount'] = tarif.prix
            except Tarif.DoesNotExist:
                raise serializers.ValidationError({'tarif': 'Tarif invalide'})

        return data

    def create(self, validated_data):
        # Remove billing_info from validated_data if present
        billing_info = validated_data.pop('billing_info', None) or self.context.get('billing_info', {})
        
        # Get annonce and tarif IDs before they are converted to instances
        annonce_id = validated_data.get('annonce')
        tarif_id = validated_data.get('tarif')
        
        # Fetch announcement details first
        try:
            if annonce_id:
                annonce = Annonce.objects.select_related('categorie', 'sous_categorie', 'utilisateur').get(id=annonce_id)
                validated_data.update({
                    'annonce_titre': annonce.titre,
                    'annonce_categorie': annonce.categorie.nom if annonce.categorie else 'Non spécifié',
                    'annonce_sous_categorie': annonce.sous_categorie.nom if annonce.sous_categorie else '',
                    'annonce_utilisateur_id': annonce.utilisateur.id if annonce.utilisateur else None
                })
        except Annonce.DoesNotExist:
            validated_data.update({
                'annonce_titre': 'Non spécifié',
                'annonce_categorie': 'Non spécifié',
                'annonce_sous_categorie': '',
                'annonce_utilisateur_id': None
            })

        # Fetch and populate tarif details
        try:
            if tarif_id:
                tarif = Tarif.objects.get(id=tarif_id)
                validated_data.update({
                    'tarif_nom': tarif.nom,
                    'tarif_prix': tarif.prix
                })
                # Set amount if not provided
                if 'amount' not in validated_data:
                    validated_data['amount'] = tarif.prix
        except Tarif.DoesNotExist:
            validated_data.update({
                'tarif_nom': 'Non spécifié',
                'tarif_prix': validated_data.get('amount', 0)
            })
        
        # Update user information from billing info or request user
        user = self.context['request'].user if 'request' in self.context else None
        
        if billing_info:
            validated_data.update({
                'user_first_name': billing_info.get('customer_name', '').strip() or (user.first_name if user else 'Non spécifié'),
                'user_last_name': billing_info.get('customer_surname', '').strip() or (user.last_name if user else 'Non spécifié'),
                'user_email': billing_info.get('customer_email', '').strip() or (user.email if user else 'no-email@example.com'),
                'user_phone': billing_info.get('customer_phone_number', '').strip() or (getattr(user, 'phone_number', '') if user else ''),
                'user_address': billing_info.get('customer_address', '').strip() or (getattr(user, 'address', '') if user else ''),
                'user_city': billing_info.get('customer_city', '').strip() or (getattr(user, 'city', '') if user else ''),
            })
        elif user:
            validated_data.update({
                'user_first_name': user.first_name or 'Non spécifié',
                'user_last_name': user.last_name or 'Non spécifié',
                'user_email': user.email or 'no-email@example.com',
                'user_phone': getattr(user, 'phone_number', '') or '',
                'user_address': getattr(user, 'address', '') or '',
                'user_city': getattr(user, 'city', '') or '',
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
        if user:
            validated_data['user'] = user

        # Create the payment instance
        instance = super().create(validated_data)
        return instance