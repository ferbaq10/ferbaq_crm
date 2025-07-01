from datetime import datetime

from django.db.models import Prefetch
from django.db.models import Q

from catalog.viewsets.base import CachedViewSet
from client.models import Client
from opportunity.models import Opportunity
from purchase.serializers import PurchaseSerializer, PurchaseWriteSerializer


class PurchaseViewSet(CachedViewSet):
    model = Opportunity
    serializer_class = PurchaseSerializer
    CLOSING_PERCENTAGE = 80
    AMOUNT_MXN = 250000
    AMOUNT_USD = 13000
    CURRENCY_MN = 1 # ID de la divisa para MN
    CURRENCY_USD = 2 # ID de la divisa para USD

    def get_queryset(self):
        return self.get_optimized_queryset()

    def get_serializer_class(self):
        return (
            PurchaseSerializer
            if self.action in ('list', 'retrieve')
            else PurchaseWriteSerializer
        )




    def get_optimized_queryset(self):
        # Optimizar consultas de oportunidad
        optimized_clients = Prefetch(
            'contact__clients',
            queryset=Client.objects.select_related('city', 'business_group')
        )

        # Optimizar datos financieros
        optimized_finance = Prefetch(
            'finance_data',
            queryset=self.model._meta.get_field('finance_data').related_model.objects.all()
        )

        # Optimizar con tipo de estado de compra
        optimized_purchase = Prefetch(
            'purchase_data',
            queryset=self.model._meta.get_field('purchase_data').related_model.objects.all()
        )

        current_year = datetime.now().year

        return (Opportunity.objects.select_related(
            # Status y tipos básicos
            'status_opportunity',
            'currency',
            'opportunityType',

            # Contacto y sus relaciones
            'contact',
            'contact__job',
            'contact__city',

            # Proyecto y todas sus relaciones en una sola consulta
            'project',
            'project__client',
            'project__client__city',
            'project__client__business_group',
            'project__specialty',
            'project__subdivision',
            'project__subdivision__division',  # Agregado: división de subdivisión
            'project__project_status',
            'project__work_cell',
            'project__work_cell__udn'  # Agregado: UDN de work_cell

        ).prefetch_related(
            optimized_finance,
            optimized_purchase,
            optimized_clients
        ).filter(
            created__year=current_year,
            closing_percentage__gte=self.CLOSING_PERCENTAGE
        ).filter(
            Q(currency_id=self.CURRENCY_MN, amount__gte=self.AMOUNT_MXN) |
            Q(currency_id=self.CURRENCY_USD, amount__gte=self.AMOUNT_USD))
                .distinct().order_by('-created'))
