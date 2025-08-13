from abc import ABC, abstractmethod
from datetime import datetime

from opportunity.models import Opportunity, FinanceOpportunity

class AbstractFinanceOpportunityFactory(ABC):
    @abstractmethod
    def create_or_update(
        self,
        opportunity: Opportunity,
        cost_subtotal: float,
        earned_amount: float,
        order_closing_date: datetime,
        oc_number: str
    ) -> tuple[FinanceOpportunity, bool]:
        """
        Crea o actualiza una instancia de FinanceOpportunity.
        Retorna un tuple con la instancia y un booleano que indica si fue creada (True) o actualizada (False).
        """
        pass