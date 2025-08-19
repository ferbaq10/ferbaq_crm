from django.utils import timezone
from datetime import datetime

from opportunity.models import Opportunity, FinanceOpportunity
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory


class DefaultFinanceOpportunityFactory(AbstractFinanceOpportunityFactory):
    def create_or_update(
        self,
        opportunity: Opportunity,
        cost_subtotal: float,
        earned_amount: float,
        order_closing_date: datetime,
        oc_number: str,
        cash_percentage: float,
        credit_percentage: float

    ) -> tuple[FinanceOpportunity, bool]:
        return FinanceOpportunity.objects.update_or_create(
            opportunity=opportunity,
            defaults={
                'cost_subtotal': cost_subtotal,
                'earned_amount': earned_amount,
                'order_closing_date': order_closing_date or timezone.now(),
                'oc_number': oc_number,
                'cash_percentage': cash_percentage,
                'credit_percentage': credit_percentage
            }
        )