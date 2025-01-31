from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.text import slugify

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email est obligatoire')
        email = self.normalize_email(email)
        username = slugify(email.split('@')[0])
        
        # Assurer un username unique
        counter = 1
        temp_username = username
        while self.model.objects.filter(username=temp_username).exists():
            temp_username = f"{username}{counter}"
            counter += 1
        username = temp_username
        
        user = self.model(email=email, username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('ANNONCEUR', 'Annonceur'),
        ('UTILISATEUR', 'Utilisateur'),
    ]

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='UTILISATEUR'
    )
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True
    )
    banner_image = models.ImageField(
        upload_to='banner_images/',
        null=True,
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.username:
            # Créer un username basé sur l'email
            base_username = self.email.split('@')[0]
            username = slugify(base_username)
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{slugify(base_username)}{counter}"
                counter += 1
            self.username = username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class Preference(models.Model):
    LANGUE_CHOICES = (
        ('FR', 'Français'),
        ('EN', 'Anglais')
    )
    
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    langue = models.CharField(max_length=2, choices=LANGUE_CHOICES, default='FR')
    notifications = models.BooleanField(default=True)
