from catalog.viewsets import AuthenticatedModelViewSet
from .models import Objetive
from .serializers import ObjetiveSerializer, ObjetiveWriteSerializer


class ObjetiveViewSet(AuthenticatedModelViewSet):
    model = Objetive
    serializer_class = ObjetiveSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ObjetiveSerializer
        return ObjetiveWriteSerializer  # Para POST, PUT, PATCH, DELETE