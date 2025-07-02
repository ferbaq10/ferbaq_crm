from opportunity.models import Opportunity
from purchase.services.interfaces import AbstractPurchaseOpportunityFactory
from purchase.models import PurchaseStatus

class DefaultPurchaseStatusFactory(AbstractPurchaseOpportunityFactory):
    def create_or_update(
        self,
        opportunity: Opportunity,
        purchase_status_type

    ) -> tuple[PurchaseStatus, bool]:
        return PurchaseStatus.objects.update_or_create(
            opportunity=opportunity,
            defaults={
                "purchase_status_type": purchase_status_type
            }
        )
