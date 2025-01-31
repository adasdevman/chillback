from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from users.models import User
from core.models import (
    Categorie, SousCategorie, Annonce,
    GaleriePhoto, Horaire, Payment, Tarif
)
import uuid

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'role')
        read_only_fields = ('id',)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        user = authenticate(
            email=data.get('email', ''),
            password=data.get('password', '')
        )
        if not user:
            raise serializers.ValidationError(_("Invalid credentials"))
        data['user'] = user
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'profile_image', 'banner_image')

class AnnonceurRegisterSerializer(RegisterSerializer):
    class Meta(RegisterSerializer.Meta):
        fields = RegisterSerializer.Meta.fields + ('role',)

    def create(self, validated_data):
        validated_data['role'] = 'ANNONCEUR'
        return super().create(validated_data)

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'ordre']

class SousCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousCategorie
        fields = ['id', 'categorie', 'nom', 'description', 'ordre']

class HoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horaire
        fields = ['id', 'jour', 'heure_ouverture', 'heure_fermeture']

class GaleriePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleriePhoto
        fields = ['id', 'image']

class TarifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarif
        fields = ['id', 'nom', 'prix']

class AnnonceSerializer(serializers.ModelSerializer):
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    photos = GaleriePhotoSerializer(many=True, read_only=True)
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'categorie', 'sous_categorie',
            'localisation', 'date_evenement', 'est_actif', 'horaires',
            'photos', 'tarifs', 'created', 'modified'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'annonce', 'amount', 'status',
            'payment_type', 'transaction_id', 'description',
            'created', 'modified'
        ]
        read_only_fields = ['user', 'transaction_id']

    def create(self, validated_data):
        validated_data['transaction_id'] = str(uuid.uuid4())
        validated_data['status'] = 'pending'
        return super().create(validated_data) 