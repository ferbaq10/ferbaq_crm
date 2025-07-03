import logging
from injector import inject
from rest_framework.exceptions import ValidationError
from catalog.models import PurchaseStatusType
from opportunity.models import Opportunity
from purchase.services.interfaces import AbstractPurchaseOpportunityFactory

logger = logging.getLogger(__name__)


class PurchaseService:
    NEGOTIATING_STATUS_ID = 4  # Id del estado de la oportunidad 'Negociando'

    @inject
    def __init__(self, purchase_factory: AbstractPurchaseOpportunityFactory):
        self.purchase_factory = purchase_factory

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
