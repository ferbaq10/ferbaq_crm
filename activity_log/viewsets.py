from django.db.models import Prefetch

from activity_log.models import ActivityLog
from activity_log.serializers import ActivityLogSerializer, ActivityLogWriteSerializer
from catalog.viewsets.base import AuthenticatedModelViewSet
from client.models import Client


class ActivityLogViewSet(AuthenticatedModelViewSet):
    model = ActivityLog
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        return self.get_optimized_queryset()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ActivityLogSerializer
        return ActivityLogWriteSerializer  # Para POST, PUT, PATCH, DELETE


    def get_optimized_queryset(self):
        # Optimizar consultas de oportunidad
        optimized_clients = Prefetch(
            'contact__clients',
            queryset=Client.objects.select_related('city', 'business_group')
        )

        # Optimizada consulta de contactos
        return ActivityLog.objects.select_related(
            # Status y tipos básicos
            'activity_type',
            'meeting_type',
            'meeting_result',
            'project',
            'project__client',
            'project__client__city',
            'project__client__business_group',
            'project__specialty',
            'project__subdivision',
            'project__subdivision__division',  # Agregado: división de subdivisión
            'project__project_status',
            'project__work_cell',
            'project__work_cell__udn',
            'contact',
            'contact__job',
            'contact__city',
            'opportunity',
            'opportunity__status_opportunity',
            'opportunity__currency',
            'opportunity__opportunityType',
            'opportunity__project',
            'opportunity__project__client',
            'opportunity__project__client__city',
            'opportunity__project__client__business_group',
            'opportunity__project__specialty',
            'opportunity__project__subdivision',
            'opportunity__project__subdivision__division',  # Agregado: división de subdivisión
            'opportunity__project__project_status',
            'opportunity__project__work_cell',
            'opportunity__project__work_cell__udn'
        ).prefetch_related(
            optimized_clients
        )