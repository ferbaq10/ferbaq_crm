import django_filters
from .models import Client


class ClientFilter(django_filters.FilterSet):
    contact = django_filters.NumberFilter(
        field_name='contacts',
        lookup_expr='exact'
    )

    class Meta:
        model = Client
        fields = {
            # Solo campos que existen en el modelo Client
            'rfc': ['icontains'],
            'company': ['icontains'],
            'is_removed': ['exact'],
        }