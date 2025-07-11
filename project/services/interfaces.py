from abc import ABC, abstractmethod
from project.models import Project


class AbstractProjectFactory(ABC):
    @abstractmethod
    def create(self, validated_data: dict) -> Project:
        pass

    @abstractmethod
    def update(self, instance: Project, validated_data: dict) -> Project:
        pass
