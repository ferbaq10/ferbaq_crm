from client.models import Client
from client.serializers import ClientSerializer, ClientWriteSerializer
from catalog.viewsets.base import CachedViewSet

class ClientViewSet(CachedViewSet):
    model = Client
    serializer_class = ClientSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ClientSerializer
        return ClientWriteSerializer  # Para POST, PUT, PATCH, DELETE
