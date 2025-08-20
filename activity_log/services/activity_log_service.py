from django.db.models import Prefetch
from django.db.models import QuerySet

from activity_log.models import ActivityLog
from activity_log.services.interfaces import AbstractActivityLogFactory
from client.models import Client
from opportunity.services.base import BaseService


class ActivityLogService(AbstractActivityLogFactory, BaseService):
    def create(self, validated_data: dict) -> ActivityLog:
        pass

    def update(self, instance: ActivityLog, validated_data: dict) -> ActivityLog:
        pass

    def get_base_queryset(self, user)->QuerySet:
        optimized_clients = Prefetch(
            'contact__clients',
            queryset=Client.objects.select_related('city', 'business_group')
        )

        queryset = ActivityLog.objects.select_related(
            'activity_type',
            'meeting_type',
            'meeting_result',
            'project',
            'project__specialty',
            'project__subdivision',
            'project__subdivision__division',
            'project__project_status',
            'project__work_cell',
            'project__work_cell__udn',
            'contact',
            'contact__job',
            'opportunity',
            'opportunity__status_opportunity',
            'opportunity__currency',
            'opportunity__opportunityType',
            'opportunity__project',
            'opportunity__project__specialty',
            'opportunity__project__subdivision',
            'opportunity__project__subdivision__division',
            'opportunity__project__project_status',
            'opportunity__project__work_cell',
            'opportunity__project__work_cell__udn'
        ).prefetch_related(
            optimized_clients
        )
        return self.add_filter_by_rol(user, queryset,
                                      workcell_filter_field="project__work_cell__users",
                                      owner_field="project__work_cell__users")
