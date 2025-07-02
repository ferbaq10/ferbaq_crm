from opportunity.models import Opportunity, FinanceOpportunity
from purchase.services.interfaces import AbstractPurchaseOpportunityFactory


class DefaultPurchaseStatusFactory(AbstractPurchaseOpportunityFactory):
    def create_or_update(
        self,
        opportunity: Opportunity,
        purchase_status_type

    ) -> tuple[FinanceOpportunity, bool]:
        return FinanceOpportunity.objects.update_or_create(
            opportunity=opportunity,
            purchase_status_type=purchase_status_type
        )
