from catalog.viewsets import AuthenticatedModelViewSet
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(AuthenticatedModelViewSet):
    model = Project
    serializer_class = ProjectSerializer