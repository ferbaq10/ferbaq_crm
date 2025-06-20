from abc import ABC, abstractmethod
from typing import Any
from opportunity.models import Opportunity, FinanceOpportunity

class AbstractFinanceOpportunityFactory(ABC):
    @abstractmethod
    def create_or_update(
        self,
        opportunity: Opportunity,
        cost_subtotal: float,
        offer_subtotal: float,
        earned_amount: float
    ) -> tuple[FinanceOpportunity, bool]:
        """
        Crea o actualiza una instancia de FinanceOpportunity.
        Retorna un tuple con la instancia y un booleano que indica si fue creada (True) o actualizada (False).
        """
        pass
