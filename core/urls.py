"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from users.viewsets import CustomTokenObtainPairView, UserViewSet

urlpatterns = [
    path('endpoint/admin/', admin.site.urls),
    path('endpoint/catalog/', include('catalog.urls')),

    path('endpoint/auth/login/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),

    path('endpoint/', include('users.urls')),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('endpoint/', include('client.urls')),
    path('endpoint/', include('contact.urls')),
    path('endpoint/', include('objetive.urls')),

    path('endpoint/', include('opportunity.urls')),

    path('endpoint/', include('project.urls')),

    path('endpoint/', include('activity_log.urls')),

    path('endpoint/', include('purchase.urls')),


]