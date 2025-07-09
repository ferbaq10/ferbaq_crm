from client.models import Client
from client.serializers import ClientSerializer, ClientWriteSerializer
from catalog.viewsets.base import CachedViewSet



class ClientViewSet(CachedViewSet):
    model = Client
    serializer_class = ClientSerializer


    def get_queryset(self):
        return self.get_optimized_queryset()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ClientSerializer
        return ClientWriteSerializer  # Para POST, PUT, PATCH, DELETE


    def get_optimized_queryset(self):
        user = self.request.user
        workcells = user.workcell.all()

        if not workcells.exists():
            return Client.objects.none()

        # Optimizada consulta de clientes
        return Client.objects.select_related(
            # Status y tipos básicos
            'city',
            'business_group'
        ).filter(
            project__work_cell__in=workcells
        ).distinct()
