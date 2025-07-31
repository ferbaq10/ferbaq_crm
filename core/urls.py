from django.contrib import admin
from django.urls import path, include
from users.viewsets import CustomTokenObtainPairView

urlpatterns = [
    path('endpoint/admin/', admin.site.urls),
    path('endpoint/auth/login/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    path('endpoint/', include([
        path('', include('users.urls')),
        path('catalog/', include('catalog.urls')),
        path('', include('client.urls')),
        path('', include('contact.urls')),
        path('', include('objetive.urls')),
        path('', include('opportunity.urls')),
        path('', include('project.urls')),
        path('', include('activity_log.urls')),
        path('', include('purchase.urls')),
    ])),
]
