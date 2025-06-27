from django.apps import AppConfig


class ClientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'client'
    verbose_name = "Clientes"

    def ready(self):
        from .signals import register_catalog_signals
        register_catalog_signals()
