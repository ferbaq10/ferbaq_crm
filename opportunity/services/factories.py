from django.utils import timezone
from opportunity.models import Opportunity, FinanceOpportunity
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory


class DefaultFinanceOpportunityFactory(AbstractFinanceOpportunityFactory):
    def create_or_update(
        self,
        opportunity: Opportunity,
        cost_subtotal: float,
        offer_subtotal: float,
        earned_amount: float
    ) -> tuple[FinanceOpportunity, bool]:
        return FinanceOpportunity.objects.update_or_create(
            opportunity=opportunity,
            defaults={
                'name': opportunity.name,
                'cost_subtotal': cost_subtotal,
                'offer_subtotal': offer_subtotal,
                'earned_amount': earned_amount,
                'order_closing_date': timezone.now(),
            }
        )
