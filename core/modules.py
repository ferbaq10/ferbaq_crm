from injector import Module, Binder, singleton
from opportunity.services.factories import DefaultFinanceOpportunityFactory
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory
from opportunity.services.opportunity_service import OpportunityService

class AppModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(AbstractFinanceOpportunityFactory, to=DefaultFinanceOpportunityFactory, scope=singleton)
        binder.bind(OpportunityService, to=OpportunityService, scope=singleton)