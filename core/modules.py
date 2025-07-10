from injector import Module, Binder, singleton

from client.services.client_service import ClientService
from client.services.factories import ClientServiceFactory
from client.services.interfaces import AbstractClientFactory
from opportunity.services.factories import DefaultFinanceOpportunityFactory, DefaultLostOpportunityFactory
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory, AbstractLostOpportunityFactory
from opportunity.services.opportunity_service import OpportunityService
from purchase.services.factories import DefaultPurchaseStatusFactory
from purchase.services.interfaces import AbstractPurchaseOpportunityFactory
from purchase.services.purchase_service import PurchaseService


class AppModule(Module):
    def configure(self, binder: Binder) -> None:
        # Para Opportunity
        binder.bind(AbstractFinanceOpportunityFactory, to=DefaultFinanceOpportunityFactory, scope=singleton)
        binder.bind(AbstractLostOpportunityFactory, to=DefaultLostOpportunityFactory, scope=singleton)

        # Para Purchase
        binder.bind(AbstractPurchaseOpportunityFactory, to=DefaultPurchaseStatusFactory, scope=singleton)

        # Nueva línea para Client
        binder.bind(AbstractClientFactory, to=ClientServiceFactory, scope=singleton)

        # Servicios
        binder.bind(OpportunityService, to=OpportunityService, scope=singleton)
        binder.bind(PurchaseService, to=PurchaseService, scope=singleton)
        binder.bind(ClientService, to=ClientService, scope=singleton)