from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from users.viewsets import CustomTokenObtainPairView
from . import views


def health(_):
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path('endpoint/graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path('endpoint/health', health),
    path('endpoint/admin/', admin.site.urls),

    path("endpoint/test-error/", views.test_error),

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
