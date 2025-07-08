import logging
from datetime import datetime

from django.db.models import Prefetch
from django.db.models import Q, QuerySet
from injector import inject
from rest_framework.exceptions import ValidationError

from catalog.constants import CurrencyIDs, StatusIDs, OpportunityFilters
from catalog.models import PurchaseStatusType
from client.models import Client
from opportunity.models import Opportunity
from purchase.services.interfaces import AbstractPurchaseOpportunityFactory

logger = logging.getLogger(__name__)


class PurchaseService:
    NEGOTIATING_STATUS_ID = 4  # Id del estado de la oportunidad 'Negociando'

    @inject
    def __init__(self, purchase_factory: AbstractPurchaseOpportunityFactory):
        self.purchase_factory = purchase_factory

    def get_filtered_queryset(self) -> QuerySet:
        current_year = datetime.now().year

        base_queryset = self.get_base_optimized_queryset()

        filters = Q(created__year=current_year)
        filters &= Q(closing_percentage__gte=OpportunityFilters.CLOSING_PERCENTAGE)
        filters &= (
                Q(currency_id=CurrencyIDs.MN, amount__gte=OpportunityFilters.AMOUNT_MN) |
                Q(currency_id=CurrencyIDs.USD, amount__gte=OpportunityFilters.AMOUNT_USD)
        )
        filters &= (
                Q(status_opportunity_id=StatusIDs.NEGOTIATING) |
                Q(status_opportunity_id=StatusIDs.WON)
        )

        return base_queryset.filter(filters).distinct().order_by('-created')

    def get_base_optimized_queryset(self):
        optimized_clients = Prefetch(
            'contact__clients',
            queryset=Client.objects.select_related('city', 'business_group')
        )

        optimized_finance = Prefetch(
            'finance_data',
            queryset=Opportunity._meta.get_field('finance_data').related_model.objects.all()
        )

        return Opportunity.objects.select_related(
            'status_opportunity',
            'currency',
            'opportunityType',
            'contact',
            'contact__job',
            'contact__city',
            'project',
            'project__client',
            'project__client__city',
            'project__client__business_group',
            'project__specialty',
            'project__subdivision',
            'project__subdivision__division',
            'project__project_status',
            'project__work_cell',
            'project__work_cell__udn',
            'purchase_data',
            'purchase_data__purchase_status_type'
        ).prefetch_related(
            optimized_clients,
            optimized_finance
        )

    def process_update(self, instance: Opportunity, request_data: dict) -> Opportunity:
        purchase_status_type_id = request_data.get("purchase_status_type")
        try:
            purchase_status_type = PurchaseStatusType.objects.get(id=purchase_status_type_id)

            purchase_status, _ = self.purchase_factory.create_or_update(
                opportunity=instance,
                purchase_status_type=purchase_status_type
            )
            instance.refresh_from_db()

            return instance
        except PurchaseStatusType.DoesNotExist:
            logger.error(f"Error al actualizar el estado de compra de la oportunidad{e}")
            raise ValidationError({"purchase_status_type": "El tipo de estatus de compra no existe."})

        except Exception as e:
            logger.error(f"Error al actualizar el estado de compra de la oportunidad{e}")
            raise
