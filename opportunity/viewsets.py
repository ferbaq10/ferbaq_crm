from catalog.viewsets import AuthenticatedModelViewSet
from .models import Opportunity, CommercialActivity
from .serializers import OpportunitySerializer, CommercialActivitySerializer, OpportunityWriteSerializer


class OpportunityViewSet(AuthenticatedModelViewSet):
    model = Opportunity
    serializer_class = OpportunitySerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return OpportunitySerializer
        return OpportunityWriteSerializer


class CommercialActivityViewSet(AuthenticatedModelViewSet):
    model = CommercialActivity
    serializer_class = CommercialActivitySerializer
