from .models import Contact
from .serializers import ContactSerializer
from catalog.viewsets import AuthenticatedModelViewSet

class ContactViewSet(AuthenticatedModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
