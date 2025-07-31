from django.apps import AppConfig

from core.utils.signals import should_skip_signal_registration


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'
    verbose_name = "Catálogo"

    def ready(self):
        if should_skip_signal_registration():
            return

        from .signals import register_catalog_signals
        register_catalog_signals()
