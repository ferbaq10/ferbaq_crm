from rest_framework.routers import DefaultRouter

from opportunity.viewsets.opportunity_document_viewsets import OpportunityDocumentViewSet
from opportunity.viewsets.opportunity_viewsets import (OpportunityViewSet, CommercialActivityViewSet)

router = DefaultRouter()
router.register(r'opportunities', OpportunityViewSet, basename='opportunities')

router.register(r'opportunities/documents', OpportunityDocumentViewSet, basename='opportunity-documents')

router.register(r'catalog/commercial-activities', CommercialActivityViewSet, basename='commercial-activities')


urlpatterns = router.urls
