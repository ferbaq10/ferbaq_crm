import logging

from django.db import transaction
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.response import Response

from catalog.viewsets.base import CachedViewSet
from client.models import Client
from client.serializers import ClientSerializer, ClientWriteSerializer
from client.services.client_service import ClientService
from core.di import injector

logger = logging.getLogger(__name__)


class ClientViewSet(CachedViewSet):
    model = Client
    serializer_class = ClientSerializer

    # Configuración específica de Client
    cache_prefix = "client"  # Override del "catalog" por defecto

    # Configuración para invalidaciones automáticas
    write_serializer_class = ClientWriteSerializer  # Para invalidaciones automáticas
    read_serializer_class = ClientSerializer  # Para respuestas optimizadas

    @cached_property
    def client_service(self) -> ClientService:
        return injector.get(ClientService)


    def get_serializer_class(self):
        """Usar serializer correcto según la acción"""
        if self.action in ['list', 'retrieve']:
            return ClientSerializer
        return ClientWriteSerializer

    def get_queryset(self):
        """Queryset optimizado específico de Client"""
        user = self.request.user
        return self.client_service.get_base_queryset(user).distinct()

    def get_actives_queryset(self, request):
        user = request.user
        return self.client_service.get_base_queryset(user).filter(is_removed=False).distinct()


    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Crear cliente optimizado - delega en perform_create"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = self.client_service.create(serializer.validated_data)

        response_serializer = ClientSerializer(client)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Update optimizado con invalidación de cache"""
        partial = kwargs.pop('partial', False)

        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        client = self.client_service.update(instance, serializer.validated_data)

        response_serializer = ClientSerializer(client)
        return Response(response_serializer.data, status=status.HTTP_200_OK)