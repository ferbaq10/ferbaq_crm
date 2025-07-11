from activity_log.services.interfaces import AbstractActivityLogFactory
from activity_log.services.activity_log_service import ActivityLogService

class ActivityLogServiceFactory:
    def create(self) -> AbstractActivityLogFactory:
        return ActivityLogService()
