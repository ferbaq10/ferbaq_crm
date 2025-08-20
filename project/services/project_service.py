from django.db.models import QuerySet

from opportunity.services.base import BaseService
from project.models import Project
from project.services.interfaces import AbstractProjectFactory


class ProjectService(AbstractProjectFactory, BaseService):
    def create(self, validated_data: dict) -> Project:
        pass

    def update(self, instance: Project, validated_data: dict) -> Project:
        pass

    def get_base_queryset(self, user)->QuerySet:
        queryset = Project.objects.select_related(
            'specialty',
            'subdivision',
            'subdivision__division',
            'project_status',
            'work_cell',
            'work_cell__udn'
        ).prefetch_related(
            'work_cell__users'
        )

        return self.add_filter_by_rol(user, queryset,
                                      workcell_filter_field = "work_cell__users",
                                      owner_field='work_cell__users')
