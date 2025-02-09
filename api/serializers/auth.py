from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'profile_image',
            'phone_number',
            'address',
            'city',
            'username'
        )

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages={
        'required': 'L\'email est requis.',
        'invalid': 'Veuillez fournir une adresse email valide.'
    })
    password = serializers.CharField(
        style={'input_type': 'password'},
        error_messages={
            'required': 'Le mot de passe est requis.'
        }
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email:
            raise serializers.ValidationError({
                'email': 'L\'email est requis.'
            })
        
        if not password:
            raise serializers.ValidationError({
                'password': 'Le mot de passe est requis.'
            })

        return {
            'email': email,
            'password': password
        }

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'first_name',
            'last_name',
            'phone_number',
            'address',
            'city',
            'role'
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            address=validated_data.get('address', ''),
            city=validated_data.get('city', ''),
            role=validated_data.get('role', 'UTILISATEUR')
        )
        return user

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_image']
        read_only_fields = ['email']

class AnnonceurRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data, role='ANNONCEUR')
        return user 