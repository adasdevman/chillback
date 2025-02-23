from rest_framework import serializers
from ..models import (
    Categorie, SousCategorie, Annonce, 
    Horaire, Tarif, GaleriePhoto, Payment
)
from .base import TimeStampedModelSerializer
from .categorie import CategorieSerializer, SousCategorieSerializer
from users.serializers import UserProfileSerializer

class HoraireSerializer(serializers.ModelSerializer):
    heure_ouverture = serializers.SerializerMethodField()
    heure_fermeture = serializers.SerializerMethodField()

    class Meta:
        model = Horaire
        fields = ['id', 'jour', 'heure_ouverture', 'heure_fermeture']

    def get_heure_ouverture(self, obj):
        return obj.heure_ouverture.strftime('%H:%M')

    def get_heure_fermeture(self, obj):
        return obj.heure_fermeture.strftime('%H:%M')

class TarifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarif
        fields = ['id', 'nom', 'prix']

class GaleriePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleriePhoto
        fields = ['id', 'image']

class AnnonceListSerializer(TimeStampedModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    photos = GaleriePhotoSerializer(many=True, read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    sous_categorie_nom = serializers.CharField(source='sous_categorie.nom', read_only=True)
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)
    annonceur = UserProfileSerializer(source='utilisateur', read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'est_actif', 'categorie',
            'sous_categorie', 'photos', 'categorie_nom',
            'sous_categorie_nom', 'horaires', 'tarifs',
            'created', 'modified', 'annonceur'
        ]

class AnnonceSerializer(TimeStampedModelSerializer):
    photos = GaleriePhotoSerializer(many=True, read_only=True)
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)
    annonceur = UserProfileSerializer(source='utilisateur', read_only=True)
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'est_actif', 'categorie_id',
            'sous_categorie_id', 'categorie', 'sous_categorie',
            'photos', 'horaires', 'tarifs', 'annonceur',
            'created', 'modified'
        ]
        read_only_fields = ['utilisateur']

    def to_internal_value(self, data):
        # First convert the data using the parent class method
        ret = super().to_internal_value(data)
        
        # Add the category IDs from the request data
        ret['categorie_id'] = data.get('categorie_id')
        ret['sous_categorie_id'] = data.get('sous_categorie_id')
        
        # Validate that they are present
        if not ret['categorie_id']:
            raise serializers.ValidationError({'categorie_id': 'Ce champ est obligatoire.'})
        if not ret['sous_categorie_id']:
            raise serializers.ValidationError({'sous_categorie_id': 'Ce champ est obligatoire.'})
        
        return ret

    def create(self, validated_data):
        # Ensure the user is set from the context
        validated_data['utilisateur'] = self.context['request'].user
        return super().create(validated_data)

class AnnonceDetailSerializer(TimeStampedModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)
    photos = GaleriePhotoSerializer(many=True, read_only=True)
    annonceur = UserProfileSerializer(source='utilisateur', read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'utilisateur', 'categorie', 'sous_categorie',
            'titre', 'description', 'localisation', 'date_evenement',
            'est_actif', 'horaires', 'tarifs', 'photos',
            'created', 'modified', 'annonceur'
        ]
        read_only_fields = ['utilisateur']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'annonce',
            'amount',
            'status',
            'payment_type',
            'tarif',
            'created',
            'modified'
        ]
        read_only_fields = ['status', 'created', 'modified']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_payment_type(self, value):
        if value not in ['ticket', 'table']:
            raise serializers.ValidationError("Le type de paiement doit être 'ticket' ou 'table'")
        return value 