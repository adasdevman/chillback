from rest_framework import serializers
from core.models import Annonce, Categorie, SousCategorie, GaleriePhoto, Payment
from core.serializers.base import TimeStampedModelSerializer

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'ordre']

class SousCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousCategorie
        fields = ['id', 'categorie', 'nom', 'description', 'ordre']

class GaleriePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleriePhoto
        fields = ['id', 'image']

class AnnonceSerializer(TimeStampedModelSerializer):
    photos = GaleriePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'est_actif', 'categorie',
            'sous_categorie', 'photos', 'created', 'modified'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

class AnnonceListSerializer(TimeStampedModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    photos = GaleriePhotoSerializer(many=True, read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    sous_categorie_nom = serializers.CharField(source='sous_categorie.nom', read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'est_actif', 'categorie',
            'sous_categorie', 'photos', 'categorie_nom',
            'sous_categorie_nom', 'created', 'modified'
        ] 