from abc import ABC, abstractmethod
from activity_log.models import ActivityLog


class AbstractActivityLogFactory(ABC):
    @abstractmethod
    def create(self, validated_data: dict) -> ActivityLog:
        pass

    @abstractmethod
    def update(self, instance: ActivityLog, validated_data: dict) -> ActivityLog:
        pass
