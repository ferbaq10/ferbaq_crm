from abc import ABC, abstractmethod
from client.models import Client


class AbstractClientFactory(ABC):
    @abstractmethod
    def create(self, validated_data: dict) -> Client:
        pass

    @abstractmethod
    def update(self, instance: Client, validated_data: dict) -> Client:
        pass
