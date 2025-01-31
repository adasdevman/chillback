from rest_framework import serializers
from ..models import (
    Categorie, SousCategorie, Annonce, 
    Horaire, Tarif, GaleriePhoto, Payment
)
from .base import TimeStampedModelSerializer
from .categorie import CategorieSerializer, SousCategorieSerializer

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

    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'est_actif', 'categorie',
            'sous_categorie', 'photos', 'categorie_nom',
            'sous_categorie_nom', 'horaires', 'tarifs',
            'created', 'modified'
        ]

class AnnonceSerializer(TimeStampedModelSerializer):
    categorie_nom = serializers.CharField(source='categorie.nom')
    sous_categorie_nom = serializers.CharField(source='sous_categorie.nom')
    photos = GaleriePhotoSerializer(many=True, read_only=True)
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'est_actif', 'categorie',
            'sous_categorie', 'categorie_nom', 'sous_categorie_nom',
            'photos', 'horaires', 'tarifs',
            'created', 'modified'
        ]

class AnnonceDetailSerializer(TimeStampedModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)
    photos = GaleriePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'utilisateur', 'categorie', 'sous_categorie',
            'titre', 'description', 'localisation', 'date_evenement',
            'est_actif', 'horaires', 'tarifs', 'photos',
            'created', 'modified'
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