from rest_framework.routers import DefaultRouter

from opportunity.viewsets import (OpportunityViewSet, CommercialActivityViewSet)

router = DefaultRouter()
router.register(r'opportunities', OpportunityViewSet, basename='opportunities')
router.register(r'catalog/commercial-activities', CommercialActivityViewSet, basename='commercial-activities')


urlpatterns = router.urls
