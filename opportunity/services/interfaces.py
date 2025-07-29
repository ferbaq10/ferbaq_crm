from abc import ABC, abstractmethod
from datetime import datetime

from catalog.models import LostOpportunityType
from opportunity.models import Opportunity, FinanceOpportunity, LostOpportunity

class AbstractFinanceOpportunityFactory(ABC):
    @abstractmethod
    def create_or_update(
        self,
        opportunity: Opportunity,
        cost_subtotal: float,
        earned_amount: float,
        order_closing_date: datetime,
    ) -> tuple[FinanceOpportunity, bool]:
        """
        Crea o actualiza una instancia de FinanceOpportunity.
        Retorna un tuple con la instancia y un booleano que indica si fue creada (True) o actualizada (False).
        """
        pass


class AbstractLostOpportunityFactory(ABC):
    @abstractmethod
    def create_or_update(
        self,
        opportunity: Opportunity,
        lost_opportunity_type: LostOpportunityType,
    ) -> tuple[LostOpportunity, bool]:
        """
        Crea o actualiza una instancia de Lost Opportunity.
        Retorna un tuple con la instancia y un booleano que indica si fue creada (True) o actualizada (False).
        """
        pass