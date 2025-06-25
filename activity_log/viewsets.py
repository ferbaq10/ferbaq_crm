from activity_log.models import ActivityLog
from activity_log.serializers import ActivityLogSerializer, ActivityLogWriteSerializer
from catalog.viewsets.base import AuthenticatedModelViewSet

class ActivityLogViewSet(AuthenticatedModelViewSet):
    model = ActivityLog
    serializer_class = ActivityLogSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ActivityLogSerializer
        return ActivityLogWriteSerializer  # Para POST, PUT, PATCH, DELETE