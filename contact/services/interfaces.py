from abc import ABC, abstractmethod
from contact.models import Contact


class AbstractContactFactory(ABC):
    @abstractmethod
    def create(self, validated_data: dict) -> Contact:
        pass

    @abstractmethod
    def update(self, instance: Contact, validated_data: dict) -> Contact:
        pass
