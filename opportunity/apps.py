from django.apps import AppConfig


class OpportunityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'opportunity'
    verbose_name = "Oportunidad"

    def ready(self):
        from .signals import register_catalog_signals
        register_catalog_signals()
