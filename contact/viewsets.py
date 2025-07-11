from django.utils.functional import cached_property

from catalog.viewsets.base import CachedViewSet
from core.di import injector
from .models import Contact
from .serializers import ContactSerializer, ContactWriteSerializer
from .services.contact_service import ContactService


class ContactViewSet(CachedViewSet):
    model = Contact
    serializer_class = ContactSerializer


    # Configuración específica de Contact
    cache_prefix = "contact"  # Override del "catalog" por defecto

    # Configuración para invalidaciones automáticas
    write_serializer_class = ContactWriteSerializer  # Para invalidaciones automáticas
    read_serializer_class = ContactSerializer  # Para respuestas optimizadas

    @cached_property
    def contact_service(self) -> ContactService:
        return injector.get(ContactService)



    def get_queryset(self):
        user = self.request.user
        return self.contact_service.get_base_queryset(user).distinct()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ContactSerializer
        return ContactWriteSerializer  # Para POST, PUT, PATCH, DELETE

    def get_actives_queryset(self, request):
        user = request.user
        return self.contact_service.get_base_queryset(user).filter(is_removed=False).distinct()

