from client.models import Client
from client.serializers import ClientSerializer, ClientWriteSerializer
from catalog.viewsets import AuthenticatedModelViewSet

class ClientViewSet(AuthenticatedModelViewSet):
    model = Client
    serializer_class = ClientSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ClientSerializer  # ← para GET
        return ClientWriteSerializer  # ← para POST/PUT/PATCH
