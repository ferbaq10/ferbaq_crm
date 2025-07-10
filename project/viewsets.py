from catalog.viewsets.base import CachedViewSet
from .models import Project
from .serializers import ProjectSerializer, ProjectWriteSerializer


class ProjectViewSet(CachedViewSet):
    model = Project
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return self.get_optimized_queryset()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ProjectSerializer
        return ProjectWriteSerializer  # Para POST, PUT, PATCH, DELETE


    def get_optimized_queryset(self):
        user = self.request.user

        return Project.objects.select_related(
            'specialty',
            'subdivision',
            'subdivision__division',  # Agregado: división de subdivisión
            'project_status',
            'work_cell',
            'work_cell__udn'
        ).filter(work_cell__users=user)