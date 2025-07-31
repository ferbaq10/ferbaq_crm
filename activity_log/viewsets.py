from django.db.models import Prefetch
from django.utils.functional import cached_property

from activity_log.models import ActivityLog
from activity_log.serializers import ActivityLogSerializer, ActivityLogWriteSerializer
from activity_log.services.activity_log_service import ActivityLogService
from catalog.viewsets.base import AuthenticatedModelViewSet
from client.models import Client
from core.di import injector


class ActivityLogViewSet(AuthenticatedModelViewSet):
    model = ActivityLog
    serializer_class = ActivityLogSerializer

    # Configuración específica de ActivityLog
    cache_prefix = "activity_log"  # Override del "catalog" por defecto

    # Configuración para invalidaciones automáticas
    write_serializer_class = ActivityLogWriteSerializer  # Para invalidaciones automáticas
    read_serializer_class = ActivityLogSerializer  # Para respuestas optimizadas

    @cached_property
    def activity_log_service(self) -> ActivityLogService:
        return injector.get(ActivityLogService)

    def get_queryset(self):
        user = self.request.user
        return self.activity_log_service.get_base_queryset(user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ActivityLogSerializer
        return ActivityLogWriteSerializer  # Para POST, PUT, PATCH, DELETE