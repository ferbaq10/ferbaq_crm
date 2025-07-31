from rest_framework.routers import DefaultRouter
from .viewsets import (
    ContactViewSet
)

router = DefaultRouter()
router.register(r'contacts', ContactViewSet, basename='contacts')


urlpatterns = router.urls
