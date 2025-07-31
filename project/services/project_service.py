from django.db.models import QuerySet

from project.models import Project
from project.services.interfaces import AbstractProjectFactory


class ProjectService(AbstractProjectFactory):
    def create(self, validated_data: dict) -> Project:
        pass

    def update(self, instance: Project, validated_data: dict) -> Project:
        pass

    def get_base_queryset(self, user)->QuerySet:
        return Project.objects.select_related(
            'specialty',
            'subdivision',
            'subdivision__division',
            'project_status',
            'work_cell',
            'work_cell__udn'
        ).prefetch_related(
            'work_cell__users'
        ).filter(work_cell__users=user)
