import django_filters
from .models import Contact


class ContactFilter(django_filters.FilterSet):
    project = django_filters.NumberFilter(
        field_name='clients__projects',
        lookup_expr='exact'
    )

    class Meta:
        model = Contact
        fields = {
            # ✅ Solo campos que existen en el modelo Contact
            'name': ['icontains'],
            'email': ['icontains'],
            'is_removed': ['exact'],
        }