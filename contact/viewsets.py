from .models import Contact
from .serializers import ContactSerializer
from catalog.viewsets import AuthenticatedModelViewSet

class ContactViewSet(AuthenticatedModelViewSet):
    model = Contact
    serializer_class = ContactSerializer
