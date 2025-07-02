from injector import Module, Binder, singleton
from opportunity.services.factories import DefaultFinanceOpportunityFactory, DefaultLostOpportunityFactory
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory, AbstractLostOpportunityFactory
from opportunity.services.opportunity_service import OpportunityService
from purchase.services.factories import DefaultPurchaseStatusFactory
from purchase.services.interfaces import AbstractPurchaseOpportunityFactory
from purchase.services.purchase_service import PurchaseService


class AppModule(Module):
    def configure(self, binder: Binder) -> None:
        # Finanzas (ya existente)
        binder.bind(AbstractFinanceOpportunityFactory, to=DefaultFinanceOpportunityFactory, scope=singleton)
        binder.bind(AbstractLostOpportunityFactory, to=DefaultLostOpportunityFactory, scope=singleton)

        # Nueva línea para Purchase
        binder.bind(AbstractPurchaseOpportunityFactory, to=DefaultPurchaseStatusFactory, scope=singleton)

        # Servicios
        binder.bind(OpportunityService, to=OpportunityService, scope=singleton)
        binder.bind(PurchaseService, to=PurchaseService, scope=singleton)