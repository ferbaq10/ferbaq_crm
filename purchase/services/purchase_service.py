from injector import inject
from opportunity.models import Opportunity
from purchase.services.interfaces import AbstractPurchaseOpportunityFactory


class PurchaseService:
    NEGOTIATING_STATUS_ID = 4  # Id del estado de la oportunidad 'Negociando'

    @inject
    def __init__(self, purchase_factory: AbstractPurchaseOpportunityFactory):
        self.purchase_factory = purchase_factory

    def process_update(self, instance: Opportunity, validated_data: dict, request_data: dict) -> Opportunity:
        status_opportunity = validated_data.get("status_opportunity")

        if status_opportunity and status_opportunity.id == self.NEGOTIATING_STATUS_ID:
            self.purchase_factory = self.purchase_factory.create_or_update(
                opportunity=instance,
                    purchase_status_type=request_data.get("purchase_status_type")
            )

        return instance