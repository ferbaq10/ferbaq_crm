from django.utils import timezone
from injector import inject
from opportunity.models import Opportunity
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory


class OpportunityService:
    GANADA_STATUS_ID = 5

    @inject
    def __init__(self, finance_factory: AbstractFinanceOpportunityFactory):
        self.finance_factory = finance_factory

    def process_update(self, instance: Opportunity, validated_data: dict, request_data: dict) -> Opportunity:
        new_status = validated_data.get("status_opportunity")

        if new_status and new_status.id != instance.status_opportunity_id:
            validated_data["date_status"] = timezone.now()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if new_status and new_status.id == self.GANADA_STATUS_ID:
            self.finance_factory.create_or_update(
                opportunity=instance,
                cost_subtotal=float(request_data.get("cost_subtotal", 0)),
                offer_subtotal=float(request_data.get("offer_subtotal", 0)),
                earned_amount=float(request_data.get("earned_amount", 0)),
            )

        return instance