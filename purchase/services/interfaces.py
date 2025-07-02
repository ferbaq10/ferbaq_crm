from abc import ABC, abstractmethod

from catalog.models import PurchaseStatusType
from opportunity.models import Opportunity
from purchase.models import PurchaseStatus


class AbstractPurchaseOpportunityFactory(ABC):
    @abstractmethod
    def create_or_update(
        self,
        opportunity: Opportunity,
        purchase_status_type: PurchaseStatusType
    ) -> tuple[PurchaseStatus, bool]:
        """
        Crea o actualiza una instancia de FinanceOpportunity.
        Retorna un tuple con la instancia y un booleano que indica si fue creada (True) o actualizada (False).
        """
        pass
