from django.apps import AppConfig


class PurchaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchase'

    def ready(self):
        from .signals import register_catalog_signals
        register_catalog_signals()
