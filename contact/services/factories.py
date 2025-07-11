from contact.services.interfaces import AbstractContactFactory
from contact.services.contact_service import ContactService

class ContactServiceFactory:
    def create(self) -> AbstractContactFactory:
        return ContactService()
