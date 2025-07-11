from django.utils.functional import cached_property

from catalog.viewsets.base import CachedViewSet
from core.di import injector
from .models import Project
from .serializers import ProjectSerializer, ProjectWriteSerializer
from .services.project_service import ProjectService


class ProjectViewSet(CachedViewSet):
    model = Project
    serializer_class = ProjectSerializer

    # Configuración específica de Project
    cache_prefix = "project"  # Override del "catalog" por defecto

    # Configuración para invalidaciones automáticas
    write_serializer_class = ProjectWriteSerializer  # Para invalidaciones automáticas
    read_serializer_class = ProjectSerializer  # Para respuestas optimizadas

    @cached_property
    def project_service(self) -> ProjectService:
        return injector.get(ProjectService)

    def get_queryset(self):
        user = self.request.user
        return self.project_service.get_base_queryset(user).distinct()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ProjectSerializer
        return ProjectWriteSerializer  # Para POST, PUT, PATCH, DELETE

    def get_actives_queryset(self, request):
        user = request.user
        return self.project_service.get_base_queryset(user).filter(is_removed=False).distinct()