from catalog.viewsets.base import CachedViewSet
from .models import Objetive
from .serializers import ObjetiveSerializer, ObjetiveWriteSerializer


class ObjetiveViewSet(CachedViewSet):
    model = Objetive
    serializer_class = ObjetiveSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ObjetiveSerializer
        return ObjetiveWriteSerializer  # Para POST, PUT, PATCH, DELETE