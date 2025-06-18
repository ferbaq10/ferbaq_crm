from catalog.viewsets import AuthenticatedModelViewSet
from .models import Project
from .serializers import ProjectSerializer, ProjectWriteSerializer


class ProjectViewSet(AuthenticatedModelViewSet):
    model = Project
    serializer_class = ProjectSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ProjectSerializer
        return ProjectWriteSerializer  # Para POST, PUT, PATCH, DELETE