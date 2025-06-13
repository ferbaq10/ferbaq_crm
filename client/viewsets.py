from client.models import Client
from client.serializers import ClientSerializer
from catalog.viewsets import AuthenticatedModelViewSet

class ClientViewSet(AuthenticatedModelViewSet):
    model = Client
    serializer_class = ClientSerializer
