from django.utils import timezone
from injector import inject
from rest_framework.exceptions import ValidationError

from catalog.models import LostOpportunityType
from opportunity.models import Opportunity
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory, AbstractLostOpportunityFactory


class OpportunityService:
    WON_STATUS_ID = 5  # ID del estado 'Ganada'

    LOST_STATUS_ID = 6  # ID del estado 'Perdida'

    @inject
    def __init__(self, finance_factory: AbstractFinanceOpportunityFactory,
                 lost_opportunity_factory: AbstractLostOpportunityFactory):
        self.finance_factory = finance_factory
        self.lost_opportunity_factory = lost_opportunity_factory

    def process_update(self, instance: Opportunity, validated_data: dict, request_data: dict) -> Opportunity:
        new_status = validated_data.get("status_opportunity")

        if new_status and new_status.id != instance.status_opportunity_id:
            validated_data["date_status"] = timezone.now()

        # Extraer objeto anidado de datos financieros (si se incluye)
        finance_data = validated_data.pop("finance_opportunity", {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if new_status and new_status.id == self.WON_STATUS_ID and finance_data:
            self.finance_factory.create_or_update(
                opportunity=instance,
                cost_subtotal=finance_data.get("cost_subtotal", 0),
                offer_subtotal=finance_data.get("offer_subtotal", 0),
                earned_amount=finance_data.get("earned_amount", 0),
                order_closing_date=finance_data.get("order_closing_date")
            )

        if new_status and new_status.id == self.LOST_STATUS_ID:
            try:
                lost_opportunity_type = LostOpportunityType.objects.get(id=request_data.get("lost_opportunity_type"))
            except LostOpportunityType.DoesNotExist:
                raise ValidationError({"lost_opportunity_type": "El tipo de oportunidad perdida no existe."})
            self.lost_opportunity_factory = self.lost_opportunity_factory.create_or_update(
                opportunity=instance,
                lost_opportunity_type=lost_opportunity_type
            )

        return instance