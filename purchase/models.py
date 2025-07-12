from django.db import models

from catalog.models import BaseModel, PurchaseStatusType
from opportunity.models import Opportunity


class PurchaseStatus(BaseModel):
    purchase_status_type = models.ForeignKey(
        PurchaseStatusType,
        on_delete=models.DO_NOTHING,
        related_name = 'purchase_status_type_data',
        verbose_name="Tipo de estado de compra"
    )

    opportunity = models.OneToOneField(
        Opportunity,
        on_delete=models.DO_NOTHING,
        related_name='purchase_data'
    )

    # history = HistoricalRecords()
