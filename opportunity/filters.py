import django_filters
from .models import Opportunity


class OpportunityFilter(django_filters.FilterSet):
    contact = django_filters.NumberFilter(
        field_name='contact',
        lookup_expr='exact'
    )
    project = django_filters.NumberFilter(
        field_name='project',
        lookup_expr='exact'
    )

    class Meta:
        model = Opportunity
        fields = {
            # Solo campos que existen en el modelo Opportunity
            'contact': ['exact'],
            'project': ['exact'],
            'name': ['icontains'],    # ?name__icontains=foo
            'is_removed': ['exact'],
        }