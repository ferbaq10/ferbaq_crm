from django.db.models import Prefetch
from django.db.models import QuerySet

from client.models import Client
from contact.models import Contact
from contact.services.interfaces import AbstractContactFactory
from opportunity.services.base import BaseService
from project.models import Project


class ContactService(AbstractContactFactory, BaseService):
    def create(self, validated_data: dict) -> Contact:
        pass

    def update(self, instance: Contact, validated_data: dict) -> Contact:
        pass

    def get_base_queryset(self, user)->QuerySet:
        # Queryset optimizado para proyectos con todas sus relaciones
        projects_qs = Project.objects.select_related(
            'work_cell__udn',
            'specialty',
            'subdivision',
            'project_status'
        ).order_by('id')

        # Queryset optimizado para clientes con sus relaciones
        clients_qs = Client.objects.select_related(
            'city',
            'business_group'
        ).prefetch_related(
            Prefetch('projects', queryset=projects_qs)
        )

        # Queryset principal de contactos
        queryset = (
            Contact.objects
            .select_related('job')
            .prefetch_related(
                Prefetch('clients', queryset=clients_qs)
            )
        )

        return self.add_filter_by_rol(
            user,
            queryset,
            workcell_filter_field="clients__projects__work_cell__users",
            owner_field="clients__projects__work_cell__users"
        )


