from rest_framework.routers import DefaultRouter
from objetive.viewsets import ObjetiveViewSet


router = DefaultRouter()
router.register(r'objetives', ObjetiveViewSet, basename='objetives')


urlpatterns = router.urls
