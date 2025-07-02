from django.utils import timezone
from datetime import datetime

from catalog.models import LostOpportunityType
from opportunity.models import Opportunity, FinanceOpportunity, LostOpportunity
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory, AbstractLostOpportunityFactory


class DefaultFinanceOpportunityFactory(AbstractFinanceOpportunityFactory):
    def create_or_update(
        self,
        opportunity: Opportunity,
        cost_subtotal: float,
        offer_subtotal: float,
        earned_amount: float,
        order_closing_date: datetime,

    ) -> tuple[FinanceOpportunity, bool]:
        return FinanceOpportunity.objects.update_or_create(
            opportunity=opportunity,
            defaults={
                'cost_subtotal': cost_subtotal,
                'offer_subtotal': offer_subtotal,
                'earned_amount': earned_amount,
                'order_closing_date': timezone.now(),
            }
        )


class DefaultLostOpportunityFactory(AbstractLostOpportunityFactory):
    def create_or_update(
        self,
        opportunity: Opportunity,
        lost_opportunity_type: LostOpportunityType,
    ) -> tuple[LostOpportunity, bool]:
        return LostOpportunity.objects.update_or_create(
            opportunity=opportunity,
            defaults={
                "lost_opportunity_type": lost_opportunity_type
            })
