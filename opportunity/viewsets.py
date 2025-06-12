from catalog.viewsets import AuthenticatedModelViewSet
from .models import Opportunity, CommercialActivity
from .serializers import OpportunitySerializer, ComercialActivitySerializer


class OpportunityViewSet(AuthenticatedModelViewSet):
    model = Opportunity
    serializer_class = OpportunitySerializer


class CommercialActivityViewSet(AuthenticatedModelViewSet):
    model = CommercialActivity
    serializer_class = ComercialActivitySerializer
