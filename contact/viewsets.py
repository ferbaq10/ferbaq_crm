from .models import Contact
from .serializers import ContactSerializer, ContactWriteSerializer
from catalog.viewsets import AuthenticatedModelViewSet

class ContactViewSet(AuthenticatedModelViewSet):
    model = Contact
    serializer_class = ContactSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:  # Para GET (lista o detalle)
            return ContactSerializer
        return ContactWriteSerializer  # Para POST, PUT, PATCH, DELETE
