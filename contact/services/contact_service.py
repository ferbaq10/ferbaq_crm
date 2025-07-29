from django.db.models import Prefetch
from django.db.models import QuerySet

from client.models import Client
from contact.models import Contact
from contact.services.interfaces import AbstractContactFactory


class ContactService(AbstractContactFactory):
    def create(self, validated_data: dict) -> Contact:
        pass

    def update(self, instance: Contact, validated_data: dict) -> Contact:
        pass

    def get_base_queryset(self, user)->QuerySet:
        return (Contact.objects.select_related(
        'job',
    ).prefetch_related(
        Prefetch(
            'clients',
            queryset=Client.objects.prefetch_related('projects')
        )
    )
                #.filter(clients__projects__work_cell__users=user)
        )


