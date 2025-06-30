from django.db.models import Prefetch

from client.models import Client
from .models import Contact
from .serializers import ContactSerializer, ContactWriteSerializer
from catalog.viewsets.base import CachedViewSet

class ContactViewSet(CachedViewSet):
    model = Contact
    serializer_class = ContactSerializer

    def get_queryset(self):
        return self.get_optimized_queryset()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ContactSerializer
        return ContactWriteSerializer  # Para POST, PUT, PATCH, DELETE


    def get_optimized_queryset(self):
        # Optimizada consulta de contactos
        return Contact.objects.select_related(
            # Status y tipos básicos
            'city',
            'job',
           ).prefetch_related(
            Prefetch('clients',
                     queryset=Client.objects.select_related('city', 'business_group'))
        )
