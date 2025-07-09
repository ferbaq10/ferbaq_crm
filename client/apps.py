from django.apps import AppConfig

from core.utils.signals import should_skip_signal_registration


class ClientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'client'
    verbose_name = "Clientes"

    def ready(self):
        if should_skip_signal_registration():
            return

        from .signals import register_catalog_signals
        register_catalog_signals()
