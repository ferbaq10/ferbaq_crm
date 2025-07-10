from client.models import Client
from client.services.interfaces import AbstractClientFactory


class ClientService(AbstractClientFactory):
    def create(self, validated_data: dict) -> Client:
        project_ids = validated_data.pop('projects', [])
        instance = Client.objects.create(**validated_data)

        if project_ids:
            instance.projects.set(project_ids)

        return instance

    def update(self, instance: Client, validated_data: dict) -> Client:
        project_ids = validated_data.pop('projects', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if project_ids is not None:
            instance.projects.set(project_ids)

        return instance

    def get_base_queryset(self, user):
        return Client.objects.select_related(
            'city',
            'business_group'
        ).prefetch_related(
            'projects'
        ).filter(projects__work_cell__users=user)
