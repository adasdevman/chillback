from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from users.models import User, Preference
from .models import (
    Annonce,
    Categorie,
    SousCategorie,
    Horaire,
    Tarif,
    GaleriePhoto,
    Payment
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'get_phone_number', 'role', 'first_name', 'last_name', 'get_date_joined', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'date_joined')
    ordering = ('-date_joined',)
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'phone_number', 'role', 'profile_image', 'banner_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'role'),
        }),
    )

    def get_phone_number(self, obj):
        return obj.phone_number if obj.phone_number else "Non renseigné"
    get_phone_number.short_description = "Téléphone"

    def get_date_joined(self, obj):
        return obj.date_joined.strftime("%d/%m/%Y %H:%M")
    get_date_joined.short_description = "Date d'inscription"

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description', 'ordre']
    search_fields = ['nom']
    ordering = ['ordre', 'nom']

@admin.register(SousCategorie)
class SousCategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'description', 'ordre']
    list_filter = ['categorie']
    search_fields = ['nom', 'categorie__nom']
    ordering = ['categorie', 'ordre', 'nom']

class HoraireInline(admin.TabularInline):
    model = Horaire
    extra = 1

class TarifInline(admin.TabularInline):
    model = Tarif
    extra = 1

class GaleriePhotoInline(admin.TabularInline):
    model = GaleriePhoto
    extra = 1

@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ['titre', 'categorie', 'sous_categorie', 'utilisateur', 'date_evenement', 'est_actif', 'created']
    list_filter = ['categorie', 'sous_categorie', 'est_actif', 'date_evenement', 'created']
    search_fields = ['titre', 'description', 'localisation', 'utilisateur__email']
    date_hierarchy = 'created'
    inlines = [HoraireInline, TarifInline, GaleriePhotoInline]
    readonly_fields = ['created', 'modified']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'description', 'localisation', 'utilisateur')
        }),
        ('Catégorisation', {
            'fields': ('categorie', 'sous_categorie')
        }),
        ('Dates', {
            'fields': ('date_evenement', 'created', 'modified')
        }),
        ('État', {
            'fields': ('est_actif',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'annonce', 'amount', 'status', 'payment_type', 'created']
    list_filter = ['status', 'payment_type', 'created']
    search_fields = ['user__email', 'transaction_id', 'description']
    readonly_fields = ['created', 'modified']
    date_hierarchy = 'created'
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('user', 'annonce', 'amount', 'description')
        }),
        ('État du paiement', {
            'fields': ('status', 'payment_type', 'transaction_id')
        }),
        ('Dates', {
            'fields': ('created', 'modified')
        }),
    )

admin.site.register(Preference)
