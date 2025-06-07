from client.models import Client
from client.serializers import ClientSerializer
from catalog.viewsets import AuthenticatedModelViewSet

class ClientViewSet(AuthenticatedModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
