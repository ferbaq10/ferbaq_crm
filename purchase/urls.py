from rest_framework.routers import DefaultRouter
from purchase.viewsets import PurchaseViewSet

router = DefaultRouter()

router.register(r'purchases', PurchaseViewSet, basename='purchases')

urlpatterns = router.urls
