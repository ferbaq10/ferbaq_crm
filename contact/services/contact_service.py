from django.db.models import Prefetch
from django.db.models import QuerySet

from client.models import Client
from contact.models import Contact
from contact.services.interfaces import AbstractContactFactory
from opportunity.services.base import BaseService


class ContactService(AbstractContactFactory, BaseService):
    def create(self, validated_data: dict) -> Contact:
        pass

    def update(self, instance: Contact, validated_data: dict) -> Contact:
        pass

    def get_base_queryset(self, user)->QuerySet:
        queryset = (Contact.objects.select_related('job').prefetch_related(
            Prefetch('clients', queryset=Client.objects.prefetch_related('projects'))))

        return self.add_filter_by_rol(user, queryset,
                                      workcell_filter_field="clients__projects__work_cell__users")


