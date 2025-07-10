from client.services.interfaces import AbstractClientFactory
from client.services.client_service import ClientService

class ClientServiceFactory:
    def create(self) -> AbstractClientFactory:
        return ClientService()
