from rest_framework.routers import DefaultRouter

from opportunity.viewsets import OpportunityViewSet, CommercialActivityViewSet

router = DefaultRouter()
router.register(r'opportunities', OpportunityViewSet, basename='opportunities')
router.register(r'catalog/commercial-activities', CommercialActivityViewSet, basename='commercial-activities')

router.register(r'catalog/lost-opportunity-type', CommercialActivityViewSet, basename='lost-opportunity-type')

urlpatterns = router.urls
