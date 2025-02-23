"""
URL configuration for chillnowback project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def redirect_to_dashboard(request):
    return redirect('dashboard:index')

urlpatterns = [
    path('', redirect_to_dashboard, name='root'),  # Redirection de l'URL racine
    path('admin/', admin.site.urls),
    path('dashboard/', include('core.urls')),
    path('api/', include('api.urls')),  # Ajout du préfixe api/
] 

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Ajouter un message de log pour confirmer que les URLs média sont configurées
    print(f"Media files will be served from {settings.MEDIA_ROOT} at URL {settings.MEDIA_URL}")
