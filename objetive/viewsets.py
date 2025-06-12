from catalog.viewsets import AuthenticatedModelViewSet
from .models import Objetive
from .serializers import ObjetiveSerializer


class ObjetiveViewSet(AuthenticatedModelViewSet):
    model = Objetive
    serializer_class = ObjetiveSerializer