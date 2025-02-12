from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    login_view, register_view, register_annonceur_view,
    profile_view, CategorieList, AnnonceList, AnnonceDetail,
    create_payment, payment_history, CinetPayWebhookView,
    check_email, mes_annonces, mes_tickets, mes_chills,
    NotificationViewSet
)

app_name = 'api'

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')

# First create the base URL patterns
urlpatterns = [
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
    path('auth/register/annonceur/', register_annonceur_view, name='register-annonceur'),
    path('profile/', profile_view, name='profile'),
    path('categories/', CategorieList.as_view(), name='category-list'),
    path('annonces/', AnnonceList.as_view(), name='annonce-list'),
    path('annonces/<int:pk>/', AnnonceDetail.as_view(), name='annonce-detail'),
    path('payments/create/', create_payment, name='create-payment'),
    path('payments/history/', payment_history, name='payment-history'),
    path('payments/webhook/cinetpay/', CinetPayWebhookView.as_view(), name='cinetpay-webhook'),
    path('auth/check-email/', check_email, name='check-email'),
    path('annonces/mes-annonces/', mes_annonces, name='mes-annonces'),
    path('annonces/mes-tickets/', mes_tickets, name='mes-tickets'),
    path('annonces/mes-chills/', mes_chills, name='mes-chills'),
]

# Then extend the urlpatterns with the router URLs
urlpatterns.extend(router.urls)