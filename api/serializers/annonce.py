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
    categorie_id = serializers.IntegerField(write_only=True)
    sous_categorie_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'est_actif', 'categorie_id',
            'sous_categorie_id', 'photos', 'created', 'modified'
        ]

    def validate(self, data):
        # Vérifier que la catégorie existe
        try:
            categorie = Categorie.objects.get(id=data['categorie_id'])
        except Categorie.DoesNotExist:
            raise serializers.ValidationError({'categorie_id': 'Cette catégorie n\'existe pas'})

        # Vérifier que la sous-catégorie existe et appartient à la catégorie
        try:
            sous_categorie = SousCategorie.objects.get(
                id=data['sous_categorie_id'],
                categorie_id=data['categorie_id']
            )
        except SousCategorie.DoesNotExist:
            raise serializers.ValidationError({'sous_categorie_id': 'Cette sous-catégorie n\'existe pas ou n\'appartient pas à la catégorie sélectionnée'})

        return data 

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