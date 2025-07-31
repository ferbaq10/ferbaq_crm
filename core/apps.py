from django.apps import AppConfig
from core.di import injector  # importas el singleton para asegurar inicialización

class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        from opportunity.services.opportunity_service import OpportunityService
        injector.get(OpportunityService)
