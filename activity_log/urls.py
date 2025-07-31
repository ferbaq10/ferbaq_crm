from django.urls import path, include
from rest_framework.routers import DefaultRouter

from activity_log.viewsets import ActivityLogViewSet

router = DefaultRouter()
router.register(r'activities-log', ActivityLogViewSet, basename='activitieslog')

urlpatterns = [
    path('', include(router.urls)),
]